package openscap

import (
	"context"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path"
	"strings"
	"syscall"
	"time"

	docker "github.com/fsouza/go-dockerclient"
	iiapi "github.com/openshift/image-inspector/pkg/api"
	"github.com/openshift/image-inspector/pkg/util"
	xmldom "github.com/subchen/go-xmldom"
)

const (
	CPE             = "oval:org.open-scap.cpe.rhel:def:"
	CPEDict         = "/usr/share/openscap/cpe/openscap-cpe-oval.xml"
	CVEUrl          = "https://www.redhat.com/security/data/metrics/ds/"
	DistCVENameFmt  = "com.redhat.rhsa-RHEL%d.ds.xml.bz2"
	ArfResultFile   = "results-arf.xml"
	HTMLResultFile  = "results.html"
	TmpDir          = "/tmp"
	Linux           = "Linux"
	OpenSCAP        = "openscap"
	ImageShortIDLen = 11
	Unknown         = "Unknown"
	LinuxVersionPH  = "Unknown"
	OpenSCAPVersion = "1.2"

	CVEDetailsUrl = "https://cve.mitre.org/cgi-bin/cvename.cgi?name="
)

var (
	RHELDistNumbers = [...]int{5, 6, 7}
	osSetEnv        = os.Setenv
)

// rhelDistFunc provides an injectable way to get the rhel dist for testing.
type rhelDistFunc func(context.Context) (int, error)

// inputCVEFunc provides an injectable way to get the cve file for testing.
type inputCVEFunc func(int) (string, error)

// chrootOscapFunc provides an injectable way to chroot and execute oscap for testing.
type chrootOscapFunc func(context.Context, ...string) ([]byte, error)

// setEnvFunc provides an injectable way to get the cve file for testing.
type setEnvFunc func() error

// OpenSCAPReport holds the both Arf and HTML versions of openscap report.
type OpenSCAPReport struct {
	ArfBytes  []byte
	HTMLBytes []byte
}

type defaultOSCAPScanner struct {
	// CVEDir is the directory where the CVE file is saved
	CVEDir string
	// ResultsDir is the directory to which the arf report will be written
	ResultsDir string
	// CVEUrlAltPath An alternative source for the cve files
	CVEUrlAltPath string

	// Image is the metadata of the inspected image
	image *docker.Image
	// ImageMountPath is the path where the image to be scanned is mounted
	imageMountPath string

	rhelDist    rhelDistFunc
	inputCVE    inputCVEFunc
	chrootOscap chrootOscapFunc
	setEnv      setEnvFunc

	// Whether or not to generate an HTML report
	HTML bool

	reports OpenSCAPReport
}

// ensure interface is implemented
var _ iiapi.Scanner = &defaultOSCAPScanner{}

// NewDefaultScanner returns a new OpenSCAP scanner
func NewDefaultScanner(cveDir, resultsDir, CVEUrlAltPath string, html bool) iiapi.Scanner {
	scanner := &defaultOSCAPScanner{
		CVEDir:        cveDir,
		ResultsDir:    resultsDir,
		CVEUrlAltPath: CVEUrlAltPath,
		HTML:          html,
	}

	scanner.rhelDist = scanner.getRHELDist
	scanner.inputCVE = scanner.getInputCVE
	scanner.chrootOscap = scanner.oscapChroot
	scanner.setEnv = scanner.setOscapChrootEnv
	scanner.reports = OpenSCAPReport{}

	return scanner
}

func (s *defaultOSCAPScanner) getRHELDist(ctx context.Context) (int, error) {
	for _, dist := range RHELDistNumbers {
		output, err := s.chrootOscap(ctx, "oval", "eval", "--id",
			fmt.Sprintf("%s%d", CPE, dist), CPEDict)
		if err != nil {
			return 0, err
		}
		if strings.Contains(string(output), fmt.Sprintf("%s%d: true", CPE, dist)) {
			return dist, nil
		}
	}
	return 0, fmt.Errorf("could not find RHEL dist")
}

func (s *defaultOSCAPScanner) getInputCVE(dist int) (string, error) {
	cveName := fmt.Sprintf(DistCVENameFmt, dist)
	cveFileName := path.Join(s.CVEDir, cveName)
	var err error
	var cveURL *url.URL
	if len(s.CVEUrlAltPath) > 0 {
		if cveURL, err = url.Parse(s.CVEUrlAltPath); err != nil {
			return "", fmt.Errorf("Could not parse CVE URL %s: %v\n",
				s.CVEUrlAltPath, err)
		}
	} else {
		cveURL, _ = url.Parse(CVEUrl)
	}
	cveURL.Path = path.Join(cveURL.Path, cveName)

	out, err := os.Create(cveFileName)
	if err != nil {
		return "", fmt.Errorf("Could not create file %s: %v\n", cveFileName, err)
	}
	defer out.Close()

	resp, err := http.Get(cveURL.String())
	if err != nil {
		return "", fmt.Errorf("Could not download file %s: %v\n", cveURL, err)
	}
	defer resp.Body.Close()

	_, err = io.Copy(out, resp.Body)
	return cveFileName, err
}

func (s *defaultOSCAPScanner) setOscapChrootEnv() error {
	for k, v := range map[string]string{
		"OSCAP_PROBE_ROOT":         s.imageMountPath,
		"OSCAP_PROBE_OS_VERSION":   LinuxVersionPH, // FIXME place holder value
		"OSCAP_PROBE_ARCHITECTURE": util.StrOrDefault(s.image.Architecture, Unknown),
		"OSCAP_PROBE_OS_NAME":      Linux,
		"OSCAP_PROBE_PRIMARY_HOST_NAME": fmt.Sprintf("docker-image-%s",
			s.image.ID[:util.Min(ImageShortIDLen, len(s.image.ID))]),
	} {
		err := osSetEnv(k, v)
		if err != nil {
			return err
		}
	}
	return nil
}

// Wrapper function for executing oscap
func (s *defaultOSCAPScanner) oscapChroot(ctx context.Context, oscapArgs ...string) ([]byte, error) {
	if err := s.setEnv(); err != nil {
		return nil, fmt.Errorf("Unable to set env variables in oscapChroot: %v", err)
	}
	cmd := exec.CommandContext(ctx, "oscap", oscapArgs...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			waitStatus := exitError.Sys().(syscall.WaitStatus)
			if waitStatus.ExitStatus() == 2 {
				// Error code 2 means that OpenSCAP had failed rules
				// For our purpose this means success
				return out, nil
			}
			return out, fmt.Errorf("OpenSCAP error: %d: %v\nInput:\n%s\nOutput:\n%s\n",
				waitStatus.ExitStatus(), err, oscapArgs, string(out))
		}
	}
	return out, err
}

func (s *defaultOSCAPScanner) Scan(ctx context.Context, mountPath string, image *docker.Image, filter iiapi.FilesFilter) ([]iiapi.Result, interface{}, error) {
	fi, err := os.Stat(mountPath)
	if err != nil || os.IsNotExist(err) || !fi.IsDir() {
		return nil, nil, fmt.Errorf("%s is not a directory, error: %v", mountPath, err)
	}
	if image == nil {
		return nil, nil, fmt.Errorf("image cannot be nil")
	}
	s.image = image
	s.imageMountPath = mountPath

	rhelDist, err := s.rhelDist(ctx)
	if err != nil {
		return nil, nil, fmt.Errorf("Unable to get RHEL distribution number: %v\n", err)
	}

	cveFileName, err := s.inputCVE(rhelDist)
	if err != nil {
		return nil, nil, fmt.Errorf("Unable to retreive the CVE file: %v\n", err)
	}

	args := []string{"xccdf", "eval", "--results-arf", path.Join(s.ResultsDir, ArfResultFile)}

	if s.HTML {
		args = append(args, "--report", path.Join(s.ResultsDir, HTMLResultFile))
	}
	log.Printf("Writing OpenSCAP results to %s", s.ResultsDir)

	args = append(args, cveFileName)

	_, err = s.chrootOscap(ctx, args...)
	if err != nil {
		return nil, nil, err
	}

	// for mock/testing
	if len(s.reports.ArfBytes) > 0 {
		return ParseResults(s.reports.ArfBytes), s.reports, nil
	}

	s.reports.ArfBytes, s.reports.HTMLBytes, err = s.readOpenSCAPReports()
	if err != nil {
		return nil, nil, err
	}

	return ParseResults(s.reports.ArfBytes), s.reports, nil
}

func (s *defaultOSCAPScanner) readOpenSCAPReports() ([]byte, []byte, error) {
	empty := []byte{}
	arfResults, err := ioutil.ReadFile(path.Join(s.ResultsDir, ArfResultFile))
	if err != nil {
		return empty, empty, err
	}
	if s.HTML {
		htmlResults, err := ioutil.ReadFile(path.Join(s.ResultsDir, HTMLResultFile))
		if err != nil {
			return empty, empty, err
		}
		return htmlResults, arfResults, nil
	}
	return arfResults, empty, nil
}

func (s *defaultOSCAPScanner) Name() string {
	return OpenSCAP
}

func ParseResults(report []byte) []iiapi.Result {
	ret := []iiapi.Result{}
	doc, err := xmldom.ParseXML(string(report))
	if err != nil {
		log.Printf("Error parsing result XML: %v", err)
		return []iiapi.Result{}
	}
	node := xmldom.Must(doc, nil).Root
	for _, c := range node.Query("//rule-result") {
		if !strings.Contains(c.GetChild("result").Text, "fail") {
			continue
		}
		result := iiapi.Result{
			Name:           OpenSCAP,
			ScannerVersion: OpenSCAPVersion,
			Timestamp:      time.Now(),
			Reference:      fmt.Sprintf("%s=%s", CVEDetailsUrl, strings.TrimSpace(c.GetChild("ident").Text)),
		}
		// If we have rule definition, we can provide more details
		if ruleDef := node.QueryOne(fmt.Sprintf("//Benchmark//Rule[@id='%s']", c.GetAttribute("idref").Value)); ruleDef != nil {
			result.Description = strings.TrimSpace(ruleDef.GetChild("title").Text)
			result.Summary = []iiapi.Summary{{Label: iiapi.Severity(ruleDef.GetAttribute("severity").Value)}}
		}
		ret = append(ret, result)
	}
	return ret
}
