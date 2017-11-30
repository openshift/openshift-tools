package clamav

import (
	"testing"

	"golang.org/x/net/context"
	"github.com/openshift/clam-scanner/pkg/clamav"
)

type fakeClamSession struct {
	t                  *testing.T
	ctx                context.Context
	path               string
	filter             clamav.FilterFiles
	waitTillDoneCalled bool
	closeCalled        bool
}

func (f *fakeClamSession) ScanPath(ctx context.Context, path string, filter clamav.FilterFiles) error {
	f.ctx = ctx
	f.path = path
	f.filter = filter
	return nil
}
func (f *fakeClamSession) WaitTillDone() {
	f.waitTillDoneCalled = true
}
func (f *fakeClamSession) Close() error {
	f.closeCalled = true
	return nil
}
func (f *fakeClamSession) GetResults() clamav.ClamdScanResult {
	return clamav.ClamdScanResult{
		Files: []clamav.ClamdFileResult{{
			Filename: "/foo/bar/usr/bin/virus",
			Result:   "boo virus found",
		}},
	}
}

func TestScan(t *testing.T) {
	ctx := context.Background()
	scanner := &ClamScanner{clamd: &fakeClamSession{t: t}}

	results, _, err := scanner.Scan(ctx, "/foo/bar", nil, nil)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if len(results) == 0 {
		t.Fatalf("expected results, got none")
	}

	// TODO: Mock this once we report real versions
	if results[0].ScannerVersion != "0.99.2" {
		t.Errorf("expected scanner version to be mock-0.1, got %q", results[0].ScannerVersion)
	}

	if results[0].Reference != "file:///usr/bin/virus" {
		t.Errorf("expected reference to be file:///usr/bin/virus, got %q", results[0].Reference)
	}

	if results[0].Description != "boo virus found" {
		t.Errorf("expected descruption to be 'boo virus found', got %q", results[0].Description)
	}
}

func TestNewScanner(t *testing.T) {
	if _, err := NewScanner("missing.socket"); err == nil {
		t.Errorf("expected socket error, got none")
	}
}

func TestName(t *testing.T) {
	// guarantee the name won't change

	scanner := &ClamScanner{clamd: &fakeClamSession{t: t}}
	if scanner.Name() != "clamav" {
		t.Fatalf("scanner name should be clamav")
	}
}
