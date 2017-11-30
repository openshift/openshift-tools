package clamav

import (
	"fmt"
	"net"
	"time"

	"github.com/golang/glog"
)

// ClamdConn is the interface for a clamd connection.
type ClamdConn interface {
	// Close closes the connection.
	Close() error

	// Read performs a non-blocking read into a newly allocated buffer and
	// returns that buffer.
	Read() ([]byte, error)

	// Write writes the specified message to clamd.
	Write(msg, oob []byte) error
}

// clamdConn is a connection to clamd.
type clamdConn struct {
	socket *net.UnixConn
}

// NewClamdConn opens a connection to clamd and returns the connection object.
func NewClamdConn(socketName string) (ClamdConn, error) {
	unixAddr := &net.UnixAddr{
		Name: socketName,
		Net:  "unix",
	}

	socket, err := net.DialUnix("unix", nil, unixAddr)
	if err != nil {
		return nil, err
	}

	conn := &clamdConn{socket: socket}

	return conn, nil
}

// Close closes the connection with clamd.
func (conn *clamdConn) Close() error {
	if conn.socket == nil {
		return nil
	}

	err := conn.socket.Close()

	conn.socket = nil

	return err
}

// Write sends the specified message to clamd.
func (conn *clamdConn) Write(msg, oob []byte) error {
	glog.V(5).Infof("> %q", msg)

	n, oobn, err := conn.socket.WriteMsgUnix(msg, oob, nil)
	if err != nil {
		return err
	}
	if n != len(msg) || oobn != len(oob) {
		return fmt.Errorf("WriteMsgUnix wrote %d + %d bytes"+
			" but should have written %d + %d",
			n, oobn, len(msg), len(oob))
	}

	return nil
}

// Read creates a buffer, reads into that buffer from clamd (using a
// non-blocking read), and returns the buffer.
func (conn *clamdConn) Read() ([]byte, error) {
	result := make([]byte, 4096)

	conn.socket.SetDeadline(time.Now().Add(time.Second))
	n, err := conn.socket.Read(result)
	if err != nil {
		return nil, err
	}

	glog.V(5).Infof("< %q", result[:n])

	return result[:n], nil
}
