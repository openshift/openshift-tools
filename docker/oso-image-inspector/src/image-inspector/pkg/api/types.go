package api

import (
	"context"
	"os"
	"time"

	docker "github.com/fsouza/go-dockerclient"
)

// OpenSCAPStatus is the status of openscap scan
type OpenSCAPStatus string

const (
	StatusNotRequested OpenSCAPStatus = "NotRequested"
	StatusSuccess      OpenSCAPStatus = "Success"
	StatusError        OpenSCAPStatus = "Error"
	// PullAlways means that image-inspector always attempts to pull the latest image.  Inspection will fail If the pull fails.
	PullAlways string = "always"
	// PullNever means that image-inspector never pulls an image, but only uses a local image.  Inspection will fail if the image isn't present
	PullNever string = "never"
	// PullIfNotPresent means that image-inspector pulls if the image isn't present on disk. Inspection will fail if the image isn't present and the pull fails.
	PullIfNotPresent string = "when-missing"
)

// The default version for the result API object
const DefaultResultsAPIVersion = "v1alpha"

// ScanResult represents the compacted result of all scans performed on the image
type ScanResult struct {
	// APIVersion represents an API version for this result
	APIVersion string `json:"apiVersion"`
	// ImageName is a full pull spec of the input image
	ImageName string `json:"imageName"`
	// ImageIUD is a SHA256 identifier of the scanned image
	// Note that we don't set the imageID when container is the target of the scan.
	ImageID string `json:"imageID,omitempty"`
	// ContainerID contains the docker container to inspect.
	ContainerID string `json:"containerID,omitempty"`
	// Results contains compacted results of various scans performed on the image.
	// Empty results means no problems were found with the given image.
	Results []Result `json:"results,omitempty"`
}

// Result represents the compacted result of a single scan
type Result struct {
	// Name is the name of the scanner that produced this result
	Name string `json:"name"`
	// ScannerVersion is the scanner version
	ScannerVersion string `json:"scannerVersion"`
	// Timestamp is the exact time this scan was performed
	Timestamp time.Time `json:"timestamp"`
	// Reference contains URL to more details about the given result
	Reference string `json:"reference"`
	// Description describes the result in human readable form
	Description string `json:"description,omitempty"`
	// Summary contains a list of severities for the given result
	Summary []Summary `json:"summary,omitempty"`
}

type Severity string

var (
	SeverityLow       Severity = "low"
	SeverityModerate  Severity = "moderate"
	SeverityImportant Severity = "important"
	SeverityCritical  Severity = "critical"
)

// Summary represents a severy of a given result. The result can have multiple severieties
// defined.
type Summary struct {
	// Label is the human readable severity (high, important, etc.)
	Label Severity
}

type OpenSCAPMetadata struct {
	Status           OpenSCAPStatus // Status of the OpenSCAP scan report
	ErrorMessage     string         // Error message from the openscap
	ContentTimeStamp string         // Timestamp for this data
}

func (osm *OpenSCAPMetadata) SetError(err error) {
	osm.Status = StatusError
	osm.ErrorMessage = err.Error()
	osm.ContentTimeStamp = string(time.Now().Format(time.RFC850))
}

var (
	ScanOptions       = []string{"openscap", "clamav"}
	PullPolicyOptions = []string{PullAlways, PullNever, PullIfNotPresent}
)

// InspectorMetadata is the metadata type with information about image-inspector's operation
type InspectorMetadata struct {
	docker.Image // Metadata about the inspected image

	// OpenSCAP describes the state of the OpenSCAP scan
	OpenSCAP *OpenSCAPMetadata
}

// APIVersions holds a slice of supported API versions.
type APIVersions struct {
	// Versions is the supported API versions
	Versions []string `json:"versions"`
}

// FilesFilter desribes callback to filter files.
type FilesFilter func(string, os.FileInfo) bool

// Scanner interface that all scanners should define.
type Scanner interface {
	// Scan will perform a scan on the given path for the given Image.
	// It should return compacted results for JSON serialization and additionally scanner
	// specific results with more details. The context object can be used to cancel the scanning process.
	Scan(ctx context.Context, path string, image *docker.Image, filter FilesFilter) ([]Result, interface{}, error)

	// Name is the scanner's name
	Name() string
}
