package inspector_test

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/fsouza/go-dockerclient"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	iicmd "github.com/openshift/image-inspector/pkg/cmd"
	. "github.com/openshift/image-inspector/pkg/inspector"
)

var _ = Describe("ImageInspector", func() {
	var (
		ii           ImageInspector
		opts         *iicmd.ImageInspectorOptions
		serve        = "localhost:8088"
		validToken   = "w599voG89897rGVDmdp12WA681r9E5948c1CJTPi8g4HGc4NWaz62k6k1K0FMxHW40H8yOO3Hoe"
		invalidToken = "asdfqwer1234"
		client       = http.Client{
			Timeout: time.Minute,
		}
	)
	//note: no expects in this block
	//we just begin the http server here
	BeforeSuite(func() {
		var err error
		opts = iicmd.NewDefaultImageInspectorOptions()
		opts.Serve = serve
		opts.AuthToken = validToken
		opts.Image = "registry.access.redhat.com/rhel7:latest"
		opts.ScanType = "openscap"
		opts.DstPath, err = ioutil.TempDir("", "")
		Expect(err).NotTo(HaveOccurred())

		ii = NewDefaultImageInspector(*opts)
		//serving blocks, so it needs to be done in a goroutine
		go func() {
			if err := ii.Inspect(); err != nil {
				panic(err)
			}
		}()
		//allow 5 minutes to pull image
		if err := waitForImage(opts.URI, opts.Image, time.Minute*5); err != nil {
			panic(err)
		}
		//allow 40s to start serving http
		if err := waitForServer(opts.Serve, time.Second*40); err != nil {
			panic(err)
		}
	})
	AfterSuite(func() {
		os.RemoveAll(opts.DstPath)
	})
	Describe(".Inspect()", func() {

		paths := []string{
			//HEALTHZ_URL_PATH,
			//API_URL_PREFIX,
			//METADATA_URL_PATH,
			//OPENSCAP_URL_PATH,
			//OPENSCAP_REPORT_URL_PATH,
			CONTENT_URL_PREFIX,
		}
		for _, path := range paths {
			Context("when user sends HTTP request to "+path, func() {
				var req *http.Request
				BeforeEach(func() {
					var err error
					req, err = http.NewRequest("GET", "http://"+serve+path, nil)
					if err != nil {
						panic(err)
					}
				})
				Context("with incorrect authentication token", func() {
					BeforeEach(func() {
						req.Header.Set("X-Auth-Token", invalidToken)
					})
					It("should fail with status http.Status BadRequest", func() {
						res, err := client.Do(req)
						Expect(err).NotTo(HaveOccurred())
						Expect(res.StatusCode).To(Equal(http.StatusUnauthorized))
					})
				})
				Context("with correct authentication token", func() {
					BeforeEach(func() {
						req.Header.Set("X-Auth-Token", validToken)
					})
					It("should authorize the request", func() {
						res, err := client.Do(req)
						Expect(err).NotTo(HaveOccurred())
						Expect(res.StatusCode).NotTo(Equal(http.StatusUnauthorized))
					})
				})
			})
		}
	})
})

func waitForImage(uri, imageName string, timeout time.Duration) error {
	client, err := docker.NewClient(uri)
	if err != nil {
		return err
	}
	errchan := make(chan error, 1)
	pollFunc := func() {
		images, err := client.ListImages(docker.ListImagesOptions{})
		if err != nil {
			errchan <- err
			return
		}
		for _, image := range images {
			for _, tag := range image.RepoTags {
				if strings.Contains(tag, imageName) {
					errchan <- nil
					return
				}
			}
		}
	}
	go func() {
		for {
			pollFunc()
			time.Sleep(time.Second * 5)
		}
	}()
	select {
	case <-time.After(timeout):
		return fmt.Errorf("waiting for image timed out after %s", timeout.String())
	case err := <-errchan:
		if err != nil {
			return err
		}
		return nil
	}
}
func waitForServer(addr string, timeout time.Duration) error {
	errchan := make(chan error, 1)
	pollFunc := func() {
		req, err := http.NewRequest("GET", "http://"+addr+"/", nil)
		if err != nil {
			panic(err)
		}
		if _, err := http.DefaultClient.Do(req); err != nil {
			if strings.Contains(err.Error(), "connection refused") {
				return //still waiting
			}
			errchan <- err
			return
		}
		errchan <- nil
		return
	}
	go func() {
		for {
			pollFunc()
			time.Sleep(time.Second * 5)
		}
	}()
	select {
	case <-time.After(timeout):
		return fmt.Errorf("waiting for sever timed out after %s", timeout.String())
	case err := <-errchan:
		if err != nil {
			return err
		}
		return nil
	}
}
