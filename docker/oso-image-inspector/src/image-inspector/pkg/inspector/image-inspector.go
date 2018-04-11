package inspector

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	docker "github.com/fsouza/go-dockerclient"

	iiapi "github.com/openshift/image-inspector/pkg/api"
	"github.com/openshift/image-inspector/pkg/clamav"
	iicmd "github.com/openshift/image-inspector/pkg/cmd"
	apiserver "github.com/openshift/image-inspector/pkg/imageserver"
	"github.com/openshift/image-inspector/pkg/openscap"
	"github.com/openshift/image-inspector/pkg/util"

	iacq "github.com/openshift/image-inspector/pkg/imageacquirer"
)

const (
	// TODO: Make this const golang style
	VERSION_TAG              = "v1"
	HEALTHZ_URL_PATH         = "/healthz"
	API_URL_PREFIX           = "/api"
	RESULT_API_URL_PATH      = "/results"
	CONTENT_URL_PREFIX       = API_URL_PREFIX + "/" + VERSION_TAG + "/content/"
	METADATA_URL_PATH        = API_URL_PREFIX + "/" + VERSION_TAG + "/metadata"
	OPENSCAP_URL_PATH        = API_URL_PREFIX + "/" + VERSION_TAG + "/openscap"
	OPENSCAP_REPORT_URL_PATH = API_URL_PREFIX + "/" + VERSION_TAG + "/openscap-report"
	OSCAP_CVE_DIR            = "/tmp"
)

var osMkdir = os.Mkdir
var ioutilTempDir = ioutil.TempDir

type containerMeta struct {
	Container *docker.Container
	Image     *docker.Image
}

// ImageInspector is the interface for all image inspectors.
type ImageInspector interface {
	// Inspect inspects and serves the image based on the ImageInspectorOptions.
	Inspect() error
}

// scanOutputs is a struct to hold all the scan outputs that needs to be served
type scanOutputs struct {
	ScanReport     []byte
	HtmlScanReport []byte
	ScanResults    iiapi.ScanResult
}

// defaultImageInspector is the default implementation of ImageInspector.
type defaultImageInspector struct {
	opts iicmd.ImageInspectorOptions
	meta iiapi.InspectorMetadata
	// an optional image server that will server content for inspection.
	imageServer apiserver.ImageServer

	scanOutputs scanOutputs

	ImageAcquirer iiapi.ImageAcquirer // ImageAcquirer that will get the image that needs scanning
}

func getAcquirer(opts *iicmd.ImageInspectorOptions) iiapi.ImageAcquirer {
	if len(opts.Container) != 0 {
		return iacq.NewDockerContainerImageAcquirer(opts.DockerSocket, opts.ScanContainerChanges)
	}
	authOpts := iacq.AuthsOptions{
		DockerCfg:    opts.DockerCfg,
		Username:     opts.Username,
		PasswordFile: opts.PasswordFile,
	}
	if opts.UseDockerSocket {
		return iacq.NewDockerImageAcquirer(opts.DockerSocket, opts.DstPath, opts.PullPolicy, authOpts)
	}
	return iacq.NewContainerLibImageAcquirer(opts.DstPath, opts.RegistryCertDir, authOpts)
}

// NewInspectorMetadata returns a new InspectorMetadata out of *docker.Image
// The OpenSCAP status will be NotRequested
func NewInspectorMetadata(imageMetadata *docker.Image) iiapi.InspectorMetadata {
	return iiapi.InspectorMetadata{
		Image: *imageMetadata,
		OpenSCAP: &iiapi.OpenSCAPMetadata{
			Status:           iiapi.StatusNotRequested,
			ErrorMessage:     "",
			ContentTimeStamp: string(time.Now().Format(time.RFC850)),
		},
	}
}

// NewDefaultImageInspector provides a new default inspector.
func NewDefaultImageInspector(opts iicmd.ImageInspectorOptions) ImageInspector {
	inspector := &defaultImageInspector{
		opts: opts,
		meta: NewInspectorMetadata(&docker.Image{}),
	}

	// if serving then set up an image server
	if len(opts.Serve) > 0 {
		if nil == opts.ImageServer {
			imageServerOpts := apiserver.ImageServerOptions{
				ServePath:         opts.Serve,
				HealthzURL:        HEALTHZ_URL_PATH,
				APIURL:            API_URL_PREFIX,
				ResultAPIUrlPath:  RESULT_API_URL_PATH,
				APIVersions:       iiapi.APIVersions{Versions: []string{VERSION_TAG}},
				MetadataURL:       METADATA_URL_PATH,
				ContentURL:        CONTENT_URL_PREFIX,
				ScanType:          opts.ScanType,
				ScanReportURL:     OPENSCAP_URL_PATH,
				HTMLScanReport:    opts.OpenScapHTML,
				HTMLScanReportURL: OPENSCAP_REPORT_URL_PATH,
				AuthToken:         opts.AuthToken,
				Chroot:            opts.Chroot,
			}
			inspector.imageServer = apiserver.NewWebdavImageServer(imageServerOpts)
		} else {
			inspector.imageServer = opts.ImageServer
		}
	}

	if nil == opts.ImageAcquirer {
		inspector.ImageAcquirer = getAcquirer(&opts)
	} else {
		inspector.ImageAcquirer = opts.ImageAcquirer
	}

	inspector.scanOutputs.ScanResults = iiapi.ScanResult{
		APIVersion: iiapi.DefaultResultsAPIVersion,
		ImageName:  inspector.opts.Image,
		Results:    []iiapi.Result{},
	}

	return inspector
}

// Inspect inspects and serves the image based on the ImageInspectorOptions.
func (i *defaultImageInspector) Inspect() error {
	err := i.acquireAndScan()
	if err != nil {
		i.meta.ImageAcquireError = err.Error()
	}

	if i.imageServer != nil {
		return i.imageServer.ServeImage(&i.meta, i.opts.DstPath, i.scanOutputs.ScanResults, i.scanOutputs.ScanReport, i.scanOutputs.HtmlScanReport)
	}

	return err
}

// AcquireAndScan acquires and scans the image based on the ImageInspectorOptions.
func (i *defaultImageInspector) acquireAndScan() error {
	var (
		scanner iiapi.Scanner
		err     error
		source  string

		filterFn iiapi.FilesFilter
	)

	ctx := context.Background()

	if len(i.opts.Container) != 0 {
		source = i.opts.Container
	} else {
		source = i.opts.Image
	}
	err, filterFn = i.acquireImage(source)
	if err != nil {
		return err
	}

	switch i.opts.ScanType {
	case "openscap":
		if i.opts.ScanResultsDir, err = util.CreateOutputDir(i.opts.ScanResultsDir, "image-inspector-scan-results-"); err != nil {
			return err
		}
		var (
			results   []iiapi.Result
			reportObj interface{}
		)
		scanner = openscap.NewDefaultScanner(OSCAP_CVE_DIR, i.opts.ScanResultsDir, i.opts.CVEUrlPath, i.opts.OpenScapHTML)
		results, reportObj, err = scanner.Scan(ctx, i.opts.DstPath, &i.meta.Image, filterFn)
		if err != nil {
			i.meta.OpenSCAP.SetError(err)
			log.Printf("DEBUG: Unable to scan image %q with OpenSCAP: %v", i.opts.Image, err)
		} else {
			i.meta.OpenSCAP.Status = iiapi.StatusSuccess
			report := reportObj.(openscap.OpenSCAPReport)
			i.scanOutputs.ScanReport = report.ArfBytes
			i.scanOutputs.HtmlScanReport = report.HTMLBytes
			i.scanOutputs.ScanResults.Results = append(i.scanOutputs.ScanResults.Results, results...)
		}

	case "clamav":
		scanner, err = clamav.NewScanner(i.opts.ClamSocket)
		if err != nil {
			return fmt.Errorf("failed to initialize clamav scanner: %v", err)
		}
		results, _, err := scanner.Scan(ctx, i.opts.DstPath, &i.meta.Image, filterFn)
		if err != nil {
			log.Printf("DEBUG: Unable to scan image %q with ClamAV: %v", i.opts.Image, err)
			return err
		}
		i.scanOutputs.ScanResults.Results = append(i.scanOutputs.ScanResults.Results, results...)

	default:
		return fmt.Errorf("unsupported scan type: %s", i.opts.ScanType)
	}

	if len(i.opts.PostResultURL) > 0 {
		if err := i.postResults(i.scanOutputs.ScanResults); err != nil {
			log.Printf("Error posting results: %v", err)
			return err
		}
	}

	return nil
}

func (i *defaultImageInspector) postTokenContent() string {
	if len(i.opts.PostResultTokenFile) == 0 {
		return ""
	}
	token, err := ioutil.ReadFile(i.opts.PostResultTokenFile)
	if err != nil {
		log.Printf("WARNING: Unable to read the %q token file: %v (no token will be used)", i.opts.PostResultTokenFile, err)
		return ""
	}
	return fmt.Sprintf("?token=%s", strings.TrimSpace(string(token)))
}

func (i *defaultImageInspector) postResults(scanResults iiapi.ScanResult) error {
	url := i.opts.PostResultURL + i.postTokenContent()
	log.Printf("Posting results to %q ...", url)
	resultJSON, err := json.Marshal(scanResults)
	if err != nil {
		return err
	}
	client := http.Client{}
	req, err := http.NewRequest("POST", url, bytes.NewReader(resultJSON))
	if err != nil {
		return err
	}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	log.Printf("DEBUG: Success: %v", resp)
	return nil
}

// acquireImage returns error and iiapi.FilesFilter for this image.
func (i *defaultImageInspector) acquireImage(source string) (error, iiapi.FilesFilter) {
	var filterFn iiapi.FilesFilter
	var err error
	i.opts.DstPath, i.meta.Image, i.scanOutputs.ScanResults, filterFn, err = i.ImageAcquirer.Acquire(source)
	return err, filterFn
}
