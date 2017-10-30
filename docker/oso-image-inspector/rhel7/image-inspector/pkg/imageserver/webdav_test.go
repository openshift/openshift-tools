package imageserver

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"

	docker "github.com/fsouza/go-dockerclient"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/openshift/image-inspector/pkg/api"
)

const (
	versionTag             = "v1"
	healthzPath            = "/healthz"
	apiPrefix              = "/api"
	contentPath            = apiPrefix + "/" + versionTag + "/content/"
	metadataPath           = apiPrefix + "/" + versionTag + "/metadata"
	openscapReportPath     = apiPrefix + "/" + versionTag + "/openscap"
	openScapHTMLReportPath = apiPrefix + "/" + versionTag + "/openscap-report"
	scanType               = "openscap"
	authToken              = "12345"
)

var _ = Describe("Webdav", func() {
	var (
		server           *httptest.Server
		options          ImageServerOptions
		dstPath          string
		dummyScanResults = api.ScanResult{
			APIVersion: api.DefaultResultsAPIVersion,
			Results:    []api.Result{},
		}
		dummyMetadata = &api.InspectorMetadata{
			Image: docker.Image{
				ID: "dummy",
			},
			OpenSCAP: &api.OpenSCAPMetadata{
				Status: api.StatusSuccess,
			},
		}
		dummyScanReport     = []byte("this is a dummy scan report")
		dummyHTMLScanReport = []byte("this is a dummy HTML scan report")
		apiVersions         = api.APIVersions{Versions: []string{versionTag}}
	)
	JustBeforeEach(func() {
		var err error
		dstPath, err = ioutil.TempDir("", "")
		Expect(err).NotTo(HaveOccurred())
		options = ImageServerOptions{
			HealthzURL:        healthzPath,
			APIURL:            apiPrefix,
			APIVersions:       apiVersions,
			MetadataURL:       metadataPath,
			ContentURL:        contentPath,
			ScanType:          scanType,
			ScanReportURL:     openscapReportPath,
			HTMLScanReport:    true,
			HTMLScanReportURL: openScapHTMLReportPath,
			AuthToken:         authToken,
			Chroot:            false,
		}
		handler, err := NewWebdavImageServer(options).(*webdavImageServer).GetHandler(dummyMetadata, dstPath, dummyScanResults, dummyScanReport, dummyHTMLScanReport)
		Expect(err).NotTo(HaveOccurred())
		server = httptest.NewServer(handler)
	})
	AfterEach(func() {
		server.Close()
		os.RemoveAll(dstPath)
	})
	Describe("Endpoints:", func() {
		var u *url.URL
		JustBeforeEach(func() {
			var err error
			u, err = url.Parse(server.URL)
			Expect(err).NotTo(HaveOccurred())
		})
		Describe("Healthz", func() {
			JustBeforeEach(func() {
				u.Path = healthzPath
			})
			Context("valid auth token", func() {
				It("returns 200 and the text \"ok\\n\"", func() {
					status, body, err := getWithAuth(u, authToken)
					Expect(err).NotTo(HaveOccurred())
					Expect(status).To(Equal(http.StatusOK))
					Expect(body).To(Equal([]byte("ok\n")))
				})
			})
			Context("invalid auth token", func() {
				It("returns 401", func() {
					status, _, err := getWithAuth(u, "asdf")
					Expect(err).NotTo(HaveOccurred())
					Expect(status).To(Equal(http.StatusUnauthorized))
				})
			})
		})
		Describe(apiPrefix, func() {
			JustBeforeEach(func() {
				u.Path = apiPrefix
			})
			It("returns a list of available api versions", func() {
				status, body, err := getWithAuth(u, authToken)
				Expect(err).NotTo(HaveOccurred())
				Expect(status).To(Equal(http.StatusOK))
				var returnedVersions api.APIVersions
				err = json.Unmarshal(body, &returnedVersions)
				Expect(err).NotTo(HaveOccurred())
				Expect(returnedVersions).To(Equal(apiVersions))
			})
		})
		Describe(metadataPath, func() {
			JustBeforeEach(func() {
				u.Path = metadataPath
			})
			It("returns the metadata the server was initialized with", func() {
				status, body, err := getWithAuth(u, authToken)
				Expect(err).NotTo(HaveOccurred())
				Expect(status).To(Equal(http.StatusOK))
				var metadata api.InspectorMetadata
				err = json.Unmarshal(body, &metadata)
				Expect(err).NotTo(HaveOccurred())
				Expect(metadata.ID).To(Equal(dummyMetadata.ID))
				Expect(metadata.OpenSCAP.Status).To(Equal(dummyMetadata.OpenSCAP.Status))
			})
		})

		Describe(openscapReportPath, func() {
			JustBeforeEach(func() {
				u.Path = openscapReportPath
			})
			Context("OpenSCAP scan succeeded", func() {
				BeforeEach(func() {
					dummyMetadata.OpenSCAP.Status = api.StatusSuccess
				})
				It("should return 200 with the scan report", func() {
					status, body, err := getWithAuth(u, authToken)
					Expect(err).NotTo(HaveOccurred())
					Expect(status).To(Equal(http.StatusOK))
					Expect(body).To(Equal(dummyScanReport))
				})
			})
			Context("OpenSCAP scan errored", func() {
				BeforeEach(func() {
					dummyMetadata.OpenSCAP.Status = api.StatusError
					dummyMetadata.OpenSCAP.ErrorMessage = "dummy error message"
				})
				It("should return 500 with the scan error message", func() {
					status, body, err := getWithAuth(u, authToken)
					Expect(err).NotTo(HaveOccurred())
					Expect(status).To(Equal(http.StatusInternalServerError))
					Expect(string(body)).To(ContainSubstring(dummyMetadata.OpenSCAP.ErrorMessage))
				})
			})
		})

		Describe(openScapHTMLReportPath, func() {
			JustBeforeEach(func() {
				u.Path = openScapHTMLReportPath
			})
			Context("OpenSCAP scan succeeded", func() {
				BeforeEach(func() {
					dummyMetadata.OpenSCAP.Status = api.StatusSuccess
				})
				It("should return 200 with the scan report", func() {
					status, body, err := getWithAuth(u, authToken)
					Expect(err).NotTo(HaveOccurred())
					Expect(status).To(Equal(http.StatusOK))
					Expect(body).To(Equal(dummyHTMLScanReport))
				})
			})
			Context("OpenSCAP scan errored", func() {
				BeforeEach(func() {
					dummyMetadata.OpenSCAP.Status = api.StatusError
					dummyMetadata.OpenSCAP.ErrorMessage = "dummy error message"
				})
				It("should return 500 with the scan error message", func() {
					status, body, err := getWithAuth(u, authToken)
					Expect(err).NotTo(HaveOccurred())
					Expect(status).To(Equal(http.StatusInternalServerError))
					Expect(string(body)).To(ContainSubstring(dummyMetadata.OpenSCAP.ErrorMessage))
				})
			})
		})
		Describe("an HTTP GET of an expected file from "+contentPath, func() {
			fileContents := "have a nice day"
			JustBeforeEach(func() {
				tmpFile, err := ioutil.TempFile(dstPath, "")
				Expect(err).NotTo(HaveOccurred())
				_, err = tmpFile.WriteString(fileContents)
				Expect(err).NotTo(HaveOccurred())
				defer tmpFile.Close()
				u.Path = contentPath + filepath.Base(tmpFile.Name())
			})
			It("should return status 200 and the contents of the file", func() {
				status, body, err := getWithAuth(u, authToken)
				Expect(err).NotTo(HaveOccurred())
				Expect(status).To(Equal(http.StatusOK))
				Expect(string(body)).To(Equal(fileContents))
			})
		})
	})
})

func getWithAuth(u *url.URL, token string) (int, []byte, error) {
	req, err := http.NewRequest("GET", u.String(), nil)
	if err != nil {
		return 0, nil, err
	}
	req.Header.Set(authTokenHeader, token)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return 0, nil, err
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return 0, nil, err
	}
	resp.Body.Close()
	return resp.StatusCode, body, nil
}
