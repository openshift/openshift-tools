package clamav

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/fsouza/go-dockerclient"
	"github.com/openshift/clam-scanner/pkg/clamav"

	"github.com/openshift/image-inspector/pkg/api"
)

const ScannerName = "clamav"

type ClamScanner struct {
	// Socket is the location of the clamav socket.
	Socket string

	clamd clamav.ClamdSession
}

var _ api.Scanner = &ClamScanner{}

func NewScanner(socket string) (api.Scanner, error) {
	// TODO: Make the ignoreNegatives configurable
	clamSession, err := clamav.NewClamdSession(socket, true)
	if err != nil {
		return nil, err
	}
	return &ClamScanner{
		Socket: socket,
		clamd:  clamSession,
	}, nil
}

// Scan will scan the image
func (s *ClamScanner) Scan(ctx context.Context, path string, image *docker.Image, filter api.FilesFilter) ([]api.Result, interface{}, error) {
	scanResults := []api.Result{}
	// Useful for debugging
	scanStarted := time.Now()
	defer func() {
		log.Printf("clamav scan took %ds (%d problems found)", int64(time.Since(scanStarted).Seconds()), len(scanResults))
	}()
	if err := s.clamd.ScanPath(ctx, path, clamav.FilterFiles(filter)); err != nil {
		return nil, nil, err
	}
	s.clamd.WaitTillDone()
	defer s.clamd.Close()

	clamResults := s.clamd.GetResults()

	for _, r := range clamResults.Files {
		r := api.Result{
			Name:           ScannerName,
			ScannerVersion: "0.99.2", // TODO: this must be returned from clam-scanner
			Timestamp:      scanStarted,
			Reference:      fmt.Sprintf("file://%s", strings.TrimPrefix(r.Filename, path)),
			Description:    r.Result,
		}
		scanResults = append(scanResults, r)
	}

	return scanResults, nil, nil
}

func (s *ClamScanner) Name() string {
	return ScannerName
}
