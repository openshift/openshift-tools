package imageserver

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"syscall"

	"golang.org/x/net/webdav"

	iiapi "github.com/openshift/image-inspector/pkg/api"
)

const (
	// chrootServePath is the path to server if we are performing a chroot
	// this probably does not belong here.
	chrootServePath = "/"
	// authTokenHeader is the custom HTTP Header used
	// to authenticate to image inspector.
	// Clients must use a custom auth header
	// instead of standard Authorization
	// because Kubernetes Proxy strips the default Auth Header
	// from requests
	authTokenHeader = "X-Auth-Token"
)

// webdavImageServer implements ImageServer.
type webdavImageServer struct {
	opts ImageServerOptions
}

// ensures this always implements the interface or fail compilation.
var _ ImageServer = &webdavImageServer{}

// NewWebdavImageServer creates a new webdav image server.
func NewWebdavImageServer(opts ImageServerOptions) ImageServer {
	return &webdavImageServer{
		opts: opts,
	}
}

// ServeImage Serves the image.
func (s *webdavImageServer) ServeImage(meta *iiapi.InspectorMetadata,
	ImageServeURL string,
	results iiapi.ScanResult,
	scanReport []byte,
	htmlScanReport []byte,
) error {
	handler, err := s.GetHandler(meta, ImageServeURL, results, scanReport, htmlScanReport)
	if err != nil {
		return fmt.Errorf("failed to initialize imageserver: %v", err)
	}
	log.Printf("Serving image content on webdav://%s%s", s.opts.ServePath, s.opts.ContentURL)
	return http.ListenAndServe(s.opts.ServePath, handler)
}

// GetHandler Returns an http.Handler that serves the scan results
// and the image using WebDAV
func (s *webdavImageServer) GetHandler(meta *iiapi.InspectorMetadata,
	ImageServeURL string,
	results iiapi.ScanResult,
	scanReport []byte,
	htmlScanReport []byte,
) (http.Handler, error) {
	mux := http.NewServeMux()
	servePath := ImageServeURL

	if len(servePath) > 0 && len(meta.ImageAcquireError) == 0 {
		if s.opts.Chroot {
			if err := syscall.Chroot(ImageServeURL); err != nil {
				return nil, fmt.Errorf("unable to chroot into %s: %v\n", ImageServeURL, err)
			}
			if err := syscall.Chdir("/"); err != nil {
				return nil, fmt.Errorf("unable to change directory into new root: %v\n", err)
			}
			servePath = chrootServePath
		} else {
			log.Printf("!!!WARNING!!! It is insecure to serve the image content without changing")
			log.Printf("root (--chroot). Absolute-path symlinks in the image can lead to disclose")
			log.Printf("information of the hosting system.")
		}
	}

	mux.HandleFunc(s.opts.HealthzURL, func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("ok\n"))
	})

	mux.HandleFunc(s.opts.APIURL, func(w http.ResponseWriter, r *http.Request) {
		body, err := json.MarshalIndent(s.opts.APIVersions, "", "  ")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Write(body)
	})

	mux.HandleFunc(s.opts.MetadataURL, func(w http.ResponseWriter, r *http.Request) {
		body, err := json.MarshalIndent(meta, "", "  ")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Write(body)
	})

	mux.HandleFunc(s.opts.ScanReportURL, func(w http.ResponseWriter, r *http.Request) {
		if s.opts.ScanType != "" && meta.OpenSCAP.Status == iiapi.StatusSuccess {
			w.Write(scanReport)
		} else {
			if meta.OpenSCAP.Status == iiapi.StatusError {
				http.Error(w, fmt.Sprintf("OpenSCAP Error: %s", meta.OpenSCAP.ErrorMessage),
					http.StatusInternalServerError)
			} else {
				http.Error(w, "OpenSCAP option was not chosen", http.StatusNotFound)
			}
		}
	})

	mux.HandleFunc(s.opts.HTMLScanReportURL, func(w http.ResponseWriter, r *http.Request) {
		if s.opts.ScanType != "" && meta.OpenSCAP.Status == iiapi.StatusSuccess && s.opts.HTMLScanReport {
			w.Write(htmlScanReport)
		} else {
			if meta.OpenSCAP.Status == iiapi.StatusError {
				http.Error(w, fmt.Sprintf("OpenSCAP Error: %s", meta.OpenSCAP.ErrorMessage),
					http.StatusInternalServerError)
			} else {
				http.Error(w, "OpenSCAP option was not chosen", http.StatusNotFound)
			}
		}
	})

	mux.Handle(s.opts.ContentURL, &webdav.Handler{
		Prefix:     s.opts.ContentURL,
		FileSystem: webdav.Dir(servePath),
		LockSystem: webdav.NewMemLS(),
	})

	return s.checkAuth(mux), nil
}

//middleware handler for checking auth
func (s *webdavImageServer) checkAuth(next http.Handler) http.Handler {
	authToken := s.opts.AuthToken
	// allow running without authorization
	if len(authToken) == 0 {
		log.Printf("!!!WARNING!!! It is insecure to serve the image content without setting")
		log.Printf("an auth token. Please set INSPECTOR_AUTH_TOKEN in your environment.")
		return next
	}

	return http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		if err := func() error {
			token := req.Header.Get(authTokenHeader)
			if len(token) == 0 {
				return fmt.Errorf("must provide %s header with this request", authTokenHeader)
			}
			if token != authToken {
				return fmt.Errorf("invalid auth token provided")
			}
			return nil
		}(); err != nil {
			http.Error(w, fmt.Sprintf("Authorization failed: %s", err.Error()), http.StatusUnauthorized)
		} else {
			next.ServeHTTP(w, req)
		}
	})
}
