package clamav

import (
	"bytes"
	"fmt"
	"io"
	"net"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"syscall"

	"github.com/golang/glog"
	"golang.org/x/net/context"
)

type FilterFiles func(string, os.FileInfo) bool

// ClamdSession is the interface for a Clamav session.
type ClamdSession interface {
	// ScanPath scans all files under the specified path. The context object
	// can be used to cancel the scan.
	ScanPath(ctx context.Context, path string, filter FilterFiles) error

	// WaitTillDone blocks until responses have been received for all the
	// files submitted for scanning.
	WaitTillDone()

	// Close closes the clamd session.
	Close() error

	// GetResults returns the scan results.
	GetResults() ClamdScanResult
}

// clamdSession keeps track of Clamav session data.
type clamdSession struct {
	// conn is the Unix domain socket connection to clamd.
	conn ClamdConn

	// partialResponse holds any partial response in case a response is
	// split across multiple reads.
	partialResponse []byte

	// closeChan is a channel by which pollResponses signals to WaitTillDone
	// that all responses have been received.
	closeChan chan bool

	// allFilesSubmitted indicates whether all files have been submitted to
	// clamd for scanning.
	allFilesSubmitted bool

	// numFilesSubmitted is the number of files that have been submitted to
	// clamd for scanning.
	numFilesSubmitted int

	// numResponsesReceived is the number of responses that have been
	// received from clamd.  There should be one response for each file
	// submitted for scanning.
	numResponsesReceived int

	// requestIDToFilename maps request ID to filename.
	// requestIDToFilename[1] is the filename of the first file submitted
	// for scanning, requestIDToFilename[2] is the filename of the second
	// file submitted, and so on.
	requestIDToFilename map[int]string

	// requestIDToFilenameMutex is a lock protecting requestIDToFilename.
	requestIDToFilenameMutex sync.Mutex

	// ignoreNegatives indicates whether negative ("OK") scan results should
	// be omitted from the results.
	ignoreNegatives bool

	// results holds the results of the scan.  It is built incrementally as
	// responses (or errors) are received from clamd.
	results ClamdScanResult
}

// ClamdScanResult holds the results of a scan.
type ClamdScanResult struct {
	// Files holds scan results for individual files.
	Files []ClamdFileResult `json:"results"`

	// Errors holds error responses received from clamd or logged internally
	// during the scan.
	Errors []string `json:"errors"`
}

// ClamdFileResult holds the scan result for a file.
type ClamdFileResult struct {
	// Filename is the name of the file.
	Filename string `json:"filename"`

	// Result is the response received from clamd for the file.
	Result string `json:"result"`

	// Errors holds any errors that arose while submitting the file to clamd
	// for scanning or reading the response from clamd.
	Errors []string `json:"errors"`
}

// IsNegative returns a Boolean value indicating whether the scan result was
// negative ("OK") or not.
func (fileResult *ClamdFileResult) IsNegative() bool {
	return fileResult.Result == "OK"
}

// NewClamdSession opens a connection to clamd, starts a session, and returns
// a session object for that session.
func NewClamdSession(socket string, ignoreNegatives bool) (ClamdSession, error) {
	conn, err := NewClamdConn(socket)
	if err != nil {
		return nil, err
	}

	err = conn.Write([]byte("zIDSESSION\000"), nil)
	if err != nil {
		return nil, err
	}

	closeChan := make(chan bool)
	requestIDToFilename := make(map[int]string)

	s := &clamdSession{
		closeChan:                closeChan,
		conn:                     conn,
		requestIDToFilename:      requestIDToFilename,
		requestIDToFilenameMutex: sync.Mutex{},
		ignoreNegatives:          ignoreNegatives,
		results: ClamdScanResult{
			Files: []ClamdFileResult{},
		},
	}

	go s.pollResponses()

	return s, nil
}

// Close ends the session with clamd and closes the connection.
func (s *clamdSession) Close() error {
	err := s.conn.Write([]byte("zEND\000"), nil)
	if err != nil {
		s.conn.Close()
		return err
	}

	return s.conn.Close()
}

// WaitTillDone waits for all responses for each file submitted to clamd to be
// received.  It should be called only after all files have been submitted.
func (s *clamdSession) WaitTillDone() {
	s.allFilesSubmitted = true

	for {
		select {
		case <-s.closeChan:
			return
		default:
		}
	}
}

// GetResults returns the scan results.
func (s *clamdSession) GetResults() ClamdScanResult {
	return s.results
}

// pollResponses polls clamd for responses, reads them, and handles them.  It
// closes closeChan and returns once all files have been submitted and all
// responses received, or when the connection to clamd is closed.
func (s *clamdSession) pollResponses() {
	defer close(s.closeChan)

	for {
		if s.allFilesSubmitted && s.numFilesSubmitted == s.numResponsesReceived {
			return
		}

		buf, err := s.conn.Read()
		if err != nil {
			if opErr, ok := err.(*net.OpError); ok && opErr.Timeout() {
				continue
			}

			s.log(err)

			if err == io.EOF {
				return
			}

			continue
		}

		s.handleResponses(buf)
	}
}

// handleResponses takes a buffer that may contain 1 or more responses from
// clamd and handles those responses individually.
func (s *clamdSession) handleResponses(buf []byte) {
	buf = append(s.partialResponse, buf...)
	s.partialResponse = nil

	for {
		end := bytes.IndexByte(buf, '\x00')
		if end <= 0 {
			s.partialResponse = buf
			return
		}

		response := string(buf[:end])
		buf = buf[end+1:]

		glog.V(6).Infof("Parsed response:\n  %#v\nremaining buffer:\n  %#v\n", response, string(buf))

		s.handleResponse(response)
	}
}

// handleResponse takes a response that was received from clamd and handles it.
func (s *clamdSession) handleResponse(response string) {
	errors := []string{}

	requestID, requestResult, err := parseClamdResponse(response)
	if err != nil {
		errors = append(errors, err.Error())
	}

	path := "<unknown>"
	if requestID != 0 {
		var ok bool

		s.requestIDToFilenameMutex.Lock()
		path, ok = s.requestIDToFilename[requestID]
		s.requestIDToFilenameMutex.Unlock()
		if !ok {
			errors = append(errors, fmt.Sprintf("request not recognized: %d", requestID))
		}

		s.numResponsesReceived++
	}

	result := ClamdFileResult{
		Filename: path,
		Result:   requestResult,
		Errors:   errors,
	}

	glog.V(6).Infof("Received scan result for request %d out of %d submitted:\n  %#v\n",
		requestID, s.numFilesSubmitted, result)

	if !s.ignoreNegatives || !result.IsNegative() {
		s.results.Files = append(s.results.Files, result)
	}
}

// parseClamdResponse takes a response that was received from clamd and parses it.
func parseClamdResponse(response string) (int, string, error) {
	glog.V(6).Infof("Parsing clamd response: %q\n", response)

	parts := strings.SplitN(response, ": ", 3)
	if len(parts) < 3 {
		return 0, "", fmt.Errorf("unexpected response from clamd: %s", response)
	}

	// Response should have the form "<requestID>: fd[<fd>]: <response>"
	// where requestID is an integer, fd[<fd>] is the file descriptor on
	// clamd's side (which is useless to us), and response is the result of
	// the clamd scan on that file descriptor.

	requestID, err := strconv.ParseInt(parts[0], 10, 0)
	if err != nil {
		return 0, "", fmt.Errorf("strconv.ParseInt failed: %s", response)
	}

	result := parts[2]

	return int(requestID), result, nil
}

// log appends an error to the scan results.
func (s *clamdSession) log(err error) {
	s.results.Errors = append(s.results.Errors, err.Error())
}

// ScanPath performs a scan on a path by walking the path and submitting files
// to clamd.  Recoverable errors are added to the scan result.  In the case of a
// non-recoverable error, an error is returned instead.
func (s *clamdSession) ScanPath(ctx context.Context, rootPath string, filter FilterFiles) error {
	walkFn := func(path string, fileInfo os.FileInfo, err error) error {
		if err != nil {
			s.log(err)
			return nil
		}

		if ctx != nil {
			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
			}
		}

		if filter != nil {
			if !filter(path, fileInfo) {
				return filepath.SkipDir
			}
		}

		if path == rootPath || !fileInfo.Mode().IsRegular() {
			return nil
		}

		if err := s.scanFile(path); err != nil {
			s.log(err)
		}

		return nil
	}

	return filepath.Walk(rootPath, walkFn)
}

// scanFile submits a file to clamd for scanning.
func (s *clamdSession) scanFile(path string) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()

	rights := syscall.UnixRights(int(f.Fd()))
	msg := []byte("zFILDES\000\000")

	err = s.conn.Write(msg, rights)
	if err != nil {
		return err
	}

	s.numFilesSubmitted++
	s.requestIDToFilenameMutex.Lock()
	s.requestIDToFilename[s.numFilesSubmitted] = path
	s.requestIDToFilenameMutex.Unlock()

	return nil
}
