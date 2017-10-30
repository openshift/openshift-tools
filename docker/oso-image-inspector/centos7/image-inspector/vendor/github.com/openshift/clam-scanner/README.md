# Clam Scanner

Clam Scanner scans files with Clamav by submitting file descriptors to a clamd
process over a Unix domain socket.

## Building

Ensure build dependencies are installed:

    $ go get github.com/golang/glog github.com/spf13/cobra github.com/spf13/pflag

Build clam-scanner using `go install`:

    $ go install

## Usage

Use the `scan` command to perform a scan.  Use the `--path` flag to specify the
path to scan, and use the `--socket` flag to specify the Unix domain socket for
clamd:

    $ clam-scanner scan --path=/path/to/scan --socket=/host/run/clamav/clamd.scan/clamd.sock
    
Use the `--omit-negative-results` flag to omit results for files with negative
("OK") results:

    $ clam-scanner scan --path=/path/to/scan --omit-negative-results

## Running as a container

Build an image using the included Dockerfile:

    $ docker build -t clam-scanner .
    
Run the new image in a privileged container with the clamd socket mounted to
`/host/run/clamd.scan/clamd.sock` and the path to be scanned mounted to
`/tmp/scan-data`:

    $ docker run -it --rm --privileged \
        -v /run/clamd.scan/clamd.sock:/run/clamd.scan/clamd.sock \
        -v /path/to/scan:/tmp/scan-data \
        clam-scanner
