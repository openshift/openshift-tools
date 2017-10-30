package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"

	iiapi "github.com/openshift/image-inspector/pkg/api"
	iicmd "github.com/openshift/image-inspector/pkg/cmd"
	ii "github.com/openshift/image-inspector/pkg/inspector"
)

func main() {
	inspectorOptions := iicmd.NewDefaultImageInspectorOptions()

	flag.StringVar(&inspectorOptions.URI, "docker", inspectorOptions.URI, "Daemon socket to connect to")
	flag.StringVar(&inspectorOptions.Image, "image", inspectorOptions.Image, "Docker image to inspect (cannot be used with the container option)")
	flag.StringVar(&inspectorOptions.Container, "container", inspectorOptions.Container, "Docker container to inspect (cannot be used with the image option)")
	flag.BoolVar(&inspectorOptions.ScanContainerChanges, "container-changes", inspectorOptions.ScanContainerChanges, "Scan only changed files inside running container")
	flag.StringVar(&inspectorOptions.DstPath, "path", inspectorOptions.DstPath, "Destination path for the image files")
	flag.StringVar(&inspectorOptions.Serve, "serve", inspectorOptions.Serve, "Host and port where to serve the image with webdav")
	flag.BoolVar(&inspectorOptions.Chroot, "chroot", inspectorOptions.Chroot, "Change root when serving the image with webdav")
	flag.Var(&inspectorOptions.DockerCfg, "dockercfg", "Location of the docker configuration files. May be specified more than once")
	flag.StringVar(&inspectorOptions.Username, "username", inspectorOptions.Username, "username for authenticating with the docker registry")
	flag.StringVar(&inspectorOptions.PasswordFile, "password-file", inspectorOptions.PasswordFile, "Location of a file that contains the password for authentication with the docker registry")
	flag.StringVar(&inspectorOptions.ScanType, "scan-type", inspectorOptions.ScanType, fmt.Sprintf("The type of the scan to be done on the inspected image. Available scan types are: %v", iiapi.ScanOptions))
	flag.StringVar(&inspectorOptions.ScanResultsDir, "scan-results-dir", inspectorOptions.ScanResultsDir, "The directory that will contain the results of the scan")
	flag.BoolVar(&inspectorOptions.OpenScapHTML, "openscap-html-report", inspectorOptions.OpenScapHTML, "Generate an OpenScap HTML report in addition to the ARF formatted report")
	flag.StringVar(&inspectorOptions.CVEUrlPath, "cve-url", inspectorOptions.CVEUrlPath, "An alternative URL source for CVE files")
	flag.StringVar(&inspectorOptions.ClamSocket, "clam-socket", inspectorOptions.ClamSocket, "Location of clamav socket file (default: '')")
	flag.StringVar(&inspectorOptions.PostResultURL, "post-results-url", inspectorOptions.PostResultURL, "After scan finish, HTTP POST the results to this URL")
	flag.StringVar(&inspectorOptions.PostResultTokenFile, "post-results-token-file", inspectorOptions.PostResultTokenFile, "If specified, content of it will be added to the POST result URL (?token=....)")
	flag.StringVar(&inspectorOptions.AuthTokenFile, "webdav-token-file", inspectorOptions.AuthTokenFile, "If specified, token used to authenticate to Image Inspector will be read from this file")
	flag.StringVar(&inspectorOptions.PullPolicy, "pull-policy", inspectorOptions.PullPolicy, fmt.Sprintf("Pull policy, default is %s, options are: %v", iiapi.PullIfNotPresent, iiapi.PullPolicyOptions))

	flag.Parse()

	if inspectorOptions.AuthTokenFile != "" {
		authToken, err := ioutil.ReadFile(inspectorOptions.AuthTokenFile)
		if err != nil {
			log.Fatalf("error reading auth token file: %v", err)
		}
		inspectorOptions.AuthToken = string(authToken)
	} else {
		inspectorOptions.AuthToken = os.Getenv("INSPECTOR_AUTH_TOKEN")
	}

	if err := inspectorOptions.Validate(); err != nil {
		log.Fatalf("Error: %v", err)
	}

	inspector := ii.NewDefaultImageInspector(*inspectorOptions)
	if err := inspector.Inspect(); err != nil {
		log.Fatalf("Error: %v", err)
	}
}
