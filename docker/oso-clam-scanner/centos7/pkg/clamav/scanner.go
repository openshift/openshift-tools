package clamav

import (
	"encoding/json"

	"github.com/golang/glog"
	"golang.org/x/net/context"
)

// ClamScanner is the interface for a scanner.
type ClamScanner interface {
	// Scan performs a scan according to parameters set in the underlying
	// implementation and returns the scan results as an array of bytes.
	Scan() ([]byte, error)
}

// clamScanner is the implementation of ClamScanner.
type clamScanner struct {
	path                string
	socket              string
	omitNegativeResults bool
}

// NewClamScanner provides a new scanner, which scans the specified path
// using a clamd process listening on the specified Unix domain socket.
func NewClamScanner(path, socket string, omitNegatives bool) ClamScanner {
	return &clamScanner{
		path:                path,
		socket:              socket,
		omitNegativeResults: omitNegatives,
	}
}

// Scan performs a scan and returns the results as a JSON-encoded byte array.
// Recoverable errors are encoded in the JSON results.  In the case of a
// non-recoverable error, an error is returned instead.
func (scanner *clamScanner) Scan() ([]byte, error) {
	glog.V(2).Infof("Scanning %q...", scanner.path)

	ses, err := NewClamdSession(scanner.socket, scanner.omitNegativeResults)
	if err != nil {
		return nil, err
	}

	err = ses.ScanPath(context.Background(), scanner.path, nil)
	if err != nil {
		ses.Close()
		return nil, err
	}

	ses.WaitTillDone()

	err = ses.Close()
	if err != nil {
		return nil, err
	}

	b, err := json.Marshal(ses.GetResults())
	if err != nil {
		return nil, err
	}

	return b, nil
}
