package cmd

import (
	"errors"
	"fmt"
	"os"

	"github.com/golang/glog"
	"github.com/openshift/clam-scanner/pkg/clamav"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
)

// ClamScanOptions is the main scanner implementation and holds the
// configuration for a clamd scan.
type ClamScanOptions struct {
	// Path is the path to scan.
	Path string

	// Socket is the path to the Unix domain socket through which
	// clam-scanner can connect to a running clamd process.
	Socket string

	// OmitNegativeResults indicates that negative results (that is, "OK"
	// results indicating nothing found) should be omitted from the results.
	OmitNegativeResults bool
}

func init() {
	RootCmd.AddCommand(NewCommandScan("scan"))
}

// NewCommandScan returns a new "scan" command.
func NewCommandScan(name string) *cobra.Command {
	options := newDefaultClamScanOptions()

	cmd := &cobra.Command{
		Use:   "scan",
		Short: "Scans files using clamd",
		Long: `Scan files for viruses using Clamav by traversing the provided path and
submitting file descriptors via a Unix domain socket to a clamd process.`,
		Run: func(cmd *cobra.Command, args []string) {
			if err := options.Complete(); err != nil {
				fmt.Fprintln(os.Stderr, err)
				return
			}

			if err := options.Validate(); err != nil {
				fmt.Fprintln(os.Stderr, err)
				return
			}

			if err := options.Run(); err != nil {
				fmt.Fprintln(os.Stderr, err)
				return
			}
		},
	}

	options.Bind(cmd.Flags())

	return cmd
}

// newDefaultClamScanOptions provides a new ClamScanOptions with default values.
func newDefaultClamScanOptions() *ClamScanOptions {
	return &ClamScanOptions{
		Path:   ".",
		Socket: "/host/run/clamd.scan/clamd.sock",
	}
}

// Bind binds the scan command's flags to the flag set.
func (o *ClamScanOptions) Bind(flag *pflag.FlagSet) {
	flag.StringVar(&o.Path, "path", o.Path, "path to scan")
	flag.StringVar(&o.Socket, "socket", o.Socket, "path to the Unix domain socket for clamd")
	flag.BoolVar(&o.OmitNegativeResults, "omit-negative-results", o.OmitNegativeResults, "omit negative (\"OK\") results")
}

// Complete completes the required options for the scan command.
func (o *ClamScanOptions) Complete() error {
	return nil
}

// Validate performs validation on options for the scan command.
func (o *ClamScanOptions) Validate() error {
	if len(o.Path) == 0 {
		return errors.New("please specify a path to scan")
	}

	if len(o.Socket) == 0 {
		return errors.New("please specify the socket for clamd")
	}

	return nil
}

// Run performs a scan and prints the results.
func (o *ClamScanOptions) Run() error {
	scanner := clamav.NewClamScanner(o.Path, o.Socket, o.OmitNegativeResults)

	out, err := scanner.Scan()
	if err != nil {
		glog.Fatalf("Error performing scanning: %v", err)
	}

	os.Stdout.Write(out)

	return nil
}
