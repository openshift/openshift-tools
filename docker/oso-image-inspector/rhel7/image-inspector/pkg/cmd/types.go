package cmd

import (
	"fmt"

	apiserver "github.com/openshift/image-inspector/pkg/imageserver"
	oscapscanner "github.com/openshift/image-inspector/pkg/openscap"

	iiapi "github.com/openshift/image-inspector/pkg/api"

	"os"

	util "github.com/openshift/image-inspector/pkg/util"
)

const DefaultDockerSocketLocation = "unix:///host/var/run/docker.sock"

// MultiStringVar is implementing flag.Value
type MultiStringVar struct {
	Values []string
}

func (sv *MultiStringVar) Set(s string) error {
	sv.Values = append(sv.Values, s)
	return nil
}

func (sv *MultiStringVar) String() string {
	return fmt.Sprintf("%v", sv.Values)
}

// ImageInspectorOptions is the main inspector implementation and holds the configuration
// for an image inspector.
type ImageInspectorOptions struct {
	// UseDockerSocket Flag to use the local docker daemon to handle images
	UseDockerSocket bool
	// DockerSocket contains the location of the docker daemon socket to connect to.
	DockerSocket string
	// Image contains the docker image to inspect.
	Image string
	// Container contains the docker container to inspect.
	Container string
	// ScanContainerChanges controls whether or not whole rootfs will be scanned.
	ScanContainerChanges bool
	// DstPath is the destination path for image files.
	DstPath string
	// Serve holds the host and port for where to serve the image with webdav.
	Serve string
	// Chroot controls whether or not a chroot is excuted when serving the image with webdav.
	Chroot bool
	// DockerCfg is the location of the docker config file.
	DockerCfg MultiStringVar
	// Username is the username for authenticating to the docker registry.
	Username string
	// PasswordFile is the location of the file containing the password for authentication to the
	// docker registry.
	PasswordFile string
	// ScanType is the type of the scan to be done on the inspected image
	ScanType string
	// ScanResultsDir is the directory that will contain the results of the scan
	ScanResultsDir string
	// OpenScapHTML controls whether or not to generate an HTML report
	// TODO: Move this into openscap plugin options.
	OpenScapHTML bool
	// CVEUrlPath An alternative source for the cve files
	// TODO: Move this into openscap plugin options.
	CVEUrlPath string
	// ClamSocket is the location of clamav socket file
	ClamSocket string
	// PostResultURL represents an URL where the image-inspector should post the results of
	// the scan.
	PostResultURL string
	// PostResultTokenFile if specified the content of the file will be added as a token to
	// the result POST URL (eg. http://foo/?token=CONTENT.
	PostResultTokenFile string
	// AuthToken is a Shared Secret used to validate HTTP Requests.
	// AuthToken can be set through AuthTokenFile or ENV
	AuthToken string
	// AuthTokenFile is the path to a file containing the AuthToken
	// If it is not provided, the AuthToken will be read from the ENV
	AuthTokenFile string
	// PullPolicy controls whether we try to pull the inspected image
	PullPolicy string
	// RegistryCertDir
	RegistryCertDir string

	// an optional image server that will serve content for inspection.
	ImageServer apiserver.ImageServer
	// ImageAcquirer that will get the image that needs scanning
	ImageAcquirer iiapi.ImageAcquirer
}

// NewDefaultImageInspectorOptions provides a new ImageInspectorOptions with default values.
func NewDefaultImageInspectorOptions() *ImageInspectorOptions {
	return &ImageInspectorOptions{
		PullPolicy:      iiapi.PullIfNotPresent,
		DockerCfg:       MultiStringVar{[]string{}},
		CVEUrlPath:      oscapscanner.CVEUrl,
		UseDockerSocket: true,
		DockerSocket:    "unix:///host/var/run/docker.sock",
		Image:           "",
		DstPath:         "",
		Serve:           "",
		Chroot:          false,
		Username:        "",
		PasswordFile:    "",
		ScanType:        "",
		ScanResultsDir:  "",
		OpenScapHTML:    false,
		RegistryCertDir: "",
	}
}

// Validate performs validation on the field settings.
func (i *ImageInspectorOptions) Validate() error {
	if i.UseDockerSocket && len(i.DockerSocket) == 0 {
		return fmt.Errorf("Docker socket connection must be specified if UseDockerSocket is set")
	}
	if len(i.Image) > 0 && len(i.Container) > 0 {
		return fmt.Errorf("options container and image are mutually exclusive")
	}
	if len(i.Image) == 0 && len(i.Container) == 0 {
		return fmt.Errorf("docker image or container must be specified to inspect")
	}
	if i.ScanContainerChanges && len(i.Container) == 0 {
		return fmt.Errorf("please specify docker container")
	}
	if len(i.DockerCfg.Values) > 0 && len(i.Username) > 0 {
		return fmt.Errorf("only specify dockercfg file or username/password pair for authentication")
	}
	if len(i.Username) > 0 && len(i.PasswordFile) == 0 {
		return fmt.Errorf("please specify password-file for the given username")
	}
	if len(i.Serve) == 0 && i.Chroot {
		return fmt.Errorf("change root can be used only when serving the image through webdav")
	}
	if len(i.ScanResultsDir) > 0 && len(i.ScanType) == 0 {
		return fmt.Errorf("scan-result-dir can be used only when spacifing scan-type")
	}
	if len(i.ScanResultsDir) > 0 {
		fi, err := os.Stat(i.ScanResultsDir)
		if err == nil && !fi.IsDir() {
			return fmt.Errorf("scan-results-dir %q is not a directory", i.ScanResultsDir)
		}
	}
	if len(i.PostResultTokenFile) > 0 && len(i.PostResultURL) == 0 {
		return fmt.Errorf("post-results-url must be set to use post-results-token-file")
	}
	if i.OpenScapHTML && (len(i.ScanType) == 0 || i.ScanType != "openscap") {
		return fmt.Errorf("openscap-html-report can be used only when specifying scan-type as \"openscap\"")
	}
	for _, fl := range append(i.DockerCfg.Values, i.PasswordFile) {
		if len(fl) > 0 {
			if _, err := os.Stat(fl); os.IsNotExist(err) {
				return fmt.Errorf("%s does not exist", fl)
			}
		}
	}
	if len(i.ScanType) > 0 {
		if !util.StringInList(i.ScanType, iiapi.ScanOptions) {
			return fmt.Errorf("%s is not one of the available scan-types which are %v",
				i.ScanType, iiapi.ScanOptions)
		}
	}
	if i.ScanType == "clamav" && len(i.ClamSocket) == 0 {
		return fmt.Errorf("clam-socket must be set to use clamav scan type")
	}

	// A valid scan-type must be specified.
	if !util.StringInList(i.ScanType, iiapi.ScanOptions) {
		return fmt.Errorf("%s is not one of the available scan-types which are %v",
			i.ScanType, iiapi.ScanOptions)
	}
	if !util.StringInList(i.PullPolicy, iiapi.PullPolicyOptions) {
		return fmt.Errorf("%s is not one of the available pull-policy options which are %v",
			i.PullPolicy, iiapi.PullPolicyOptions)
	}

	if len(i.RegistryCertDir) > 0 {
		if i.UseDockerSocket {
			return fmt.Errorf("Can't use docker daemon with provider certificates [--use-docker, --cert-path] are mutually exclusive")
		}
		if _, err := os.Stat(i.RegistryCertDir); os.IsNotExist(err) {
			return fmt.Errorf("The provided cert path, %s , does not exists", i.RegistryCertDir)
		}
	}
	return nil
}
