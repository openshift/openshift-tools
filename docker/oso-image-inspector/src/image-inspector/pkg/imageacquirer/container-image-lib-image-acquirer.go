package imageacquirer

import (
	"bufio"
	"compress/gzip"
	"fmt"
	"github.com/opencontainers/go-digest"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	docker "github.com/fsouza/go-dockerclient"
	iiapi "github.com/openshift/image-inspector/pkg/api"
	"github.com/openshift/image-inspector/pkg/util"

	"github.com/containers/image/copy"
	"github.com/containers/image/directory"
	"github.com/containers/image/manifest"
	"github.com/containers/image/signature"
	"github.com/containers/image/transports/alltransports"
	"github.com/containers/image/types"
)

const (
	DOCKER_CERTS_DIR = "/etc/docker/certs.d"
)

type containerLibImageAcquirer struct {
	dstPath         string       // dstPath for the extraction of the image
	RegistryCertDir string       // RegistryCertDir
	Auths           AuthsOptions // Sources for authentications with docker
}

func (clia *containerLibImageAcquirer) Acquire(source string) (string, docker.Image, iiapi.ScanResult, iiapi.FilesFilter, error) {
	inspectInfo, imageDigest, err := clia.pullImage(source)
	if err != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil, err
	}

	log.Println("Extracting Image")
	if err := clia.extractDownloadedImage(inspectInfo.Layers); err != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil, fmt.Errorf("extracting downloaded image: %v ", err)
	}

	imageMetadata := inspectInfoToDockerImage(inspectInfo, imageDigest)

	scanResults := iiapi.ScanResult{
		APIVersion: iiapi.DefaultResultsAPIVersion,
		ImageName:  source,
		ImageID:    imageMetadata.ID,
		Results:    []iiapi.Result{},
	}
	return clia.dstPath, imageMetadata, scanResults, nil, nil
}

// extractDownloadedImage will untar all the layer tar files specified in 'info'
func (clia *containerLibImageAcquirer) extractDownloadedImage(layers []string) error {
	for _, layer := range layers {
		split := strings.SplitN(layer, ":", 2)
		if len(split) < 2 {
			return fmt.Errorf("invalid format for layer name: %s", layer)
		}
		baseName := split[1]
		filename := filepath.Join(clia.dstPath, baseName+".tar")
		destDir := clia.dstPath
		log.Printf("Untar %s\n", filename)
		if err := UntarGzLayer(filename, destDir); err != nil {
			return fmt.Errorf("extracting gzipped layer tarball: %v", err)
		}
	}
	return nil
}

// inspectInfoToDockerImage will convert the information in info of type ImageInspectInfo to
// imageDigest which is of type Digest.
func inspectInfoToDockerImage(info *types.ImageInspectInfo, imageDigest digest.Digest) docker.Image {
	return docker.Image{
		ID:            "",
		RepoDigests:   []string{string(imageDigest)},
		RepoTags:      []string{info.Tag},
		Created:       info.Created,
		Architecture:  info.Architecture,
		DockerVersion: info.DockerVersion,
	}
}

func (clia *containerLibImageAcquirer) pullImage(source string) (*types.ImageInspectInfo, digest.Digest, error) {
	var srcRef types.ImageReference
	policy := &signature.Policy{
		Default: []signature.PolicyRequirement{signature.NewPRInsecureAcceptAnything()},
	}
	policyContext, err := signature.NewPolicyContext(policy)
	if err != nil {
		return nil, "", fmt.Errorf("creating context for policy %v: %v", policy, err)
	}
	defer policyContext.Destroy()

	srcRef, err = alltransports.ParseImageName(source)
	if err != nil {
		var otherErr error
		source = "docker://" + source
		srcRef, otherErr = alltransports.ParseImageName(source)
		if nil != otherErr {
			return nil, "", fmt.Errorf("invalid source name %s: %v", source, err)
		}
	}

	certPath, err := clia.certPath(source)
	if err != nil {
		return nil, "", fmt.Errorf("finding certificate path: %v", err)
	}
	sourceCtx := &types.SystemContext{
		DockerCertPath: certPath,
	}

	if clia.dstPath, err = util.CreateOutputDir(clia.dstPath, "image-inspector-"); err != nil {
		return nil, "", fmt.Errorf("creating output dir: %v", err)
	}
	destRef, err := directory.NewReference(clia.dstPath)
	if err != nil {
		return nil, "", fmt.Errorf("invalid destination name %s: %v", clia.dstPath, err)
	}

	imagePullAuths, err := getAuthConfigs(clia.Auths)
	if err != nil {
		return nil, "", fmt.Errorf("getting registry auth config: %v", err)
	}

	// Try all the possible auths from the config file
	log.Println("Pulling image")
	for name, auth := range imagePullAuths.Configs {
		sourceCtx.DockerAuthConfig = &types.DockerAuthConfig{
			Username: auth.Username,
			Password: auth.Password,
		}
		reportReader, reportWriter := io.Pipe()
		// print progress from reportWriter
		go func() {
			lineReader := bufio.NewReader(reportReader)
			buffered := []byte{}
			last := time.Now()
			for {
				b, err := lineReader.ReadByte()
				if err != nil {
					return
				}
				if b == byte('\n') {
					log.Printf("%s", buffered)
					buffered = []byte{}
				}
				buffered = append(buffered, b)
				if b == byte(']') {
					if time.Since(last) > PULL_LOG_INTERVAL_SEC {
						log.Printf("%s", buffered)
						last = time.Now()
					}
					buffered = []byte{}
				}
			}
		}()
		err = copy.Image(policyContext, destRef, srcRef, &copy.Options{
			RemoveSignatures: false,
			SignBy:           "",
			ReportWriter:     reportWriter,
			SourceCtx:        sourceCtx,
			DestinationCtx:   nil,
			ProgressInterval: PULL_LOG_INTERVAL_SEC,
		})
		reportWriter.Close()
		if err == nil {
			break
		}
		log.Printf("Authentication with %s failed: %v", name, err)
	}

	if err != nil {
		return nil, "", fmt.Errorf("pulling docker image: %v\n", err)
	}

	img, err := srcRef.NewImage(sourceCtx)
	if err != nil {
		return nil, "", fmt.Errorf(": %v", err)
	}

	log.Println("Reading image manifest")
	rawManifest, _, err := img.Manifest()
	if err != nil {
		return nil, "", fmt.Errorf("reading image manifest: %v ", err)
	}
	imageDigest, err := manifest.Digest(rawManifest)
	if err != nil {
		return nil, "", fmt.Errorf("parsing image manifest: %v ", err)
	}

	inspectInfo, err := img.Inspect()
	if err != nil {
		return nil, "", fmt.Errorf("inspecting copied image Manifest: %v ", err)
	}

	return inspectInfo, imageDigest, nil
}

// certPath will try to extract the registry name from the image and return
// "/etc/docker/certs.d/<REGISTRY_NAME>" if this path exists or nil otherwise.
func (clia *containerLibImageAcquirer) certPath(fullImageName string) (string, error) {
	if len(clia.RegistryCertDir) > 0 {
		return clia.RegistryCertDir, nil
	}

	// try to find certificates from docker
	sourceName := strings.SplitN(fullImageName, "://", 2)
	name := sourceName[len(sourceName)-1]
	names := strings.SplitN(name, "/", 2)
	certsPath := filepath.Join(DOCKER_CERTS_DIR, names[0])
	if _, err := os.Stat(certsPath); err != nil {
		if os.IsNotExist(err) {
			return "", nil
		}
		return "", err
	}
	return certsPath, nil
}

// UntarGzLayer attempts to read filename as a gzipped
// stream of data, processing the decompressed data as
// a tar archive. the contents of the tar archive ar
// extracted to destination directory.
// whiteout files that are encountered are dealt with
// specially (see https://github.com/opencontainers/image-spec/blob/master/layer.md#opaque-whiteout)
func UntarGzLayer(filename, destination string) error {
	f, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer f.Close()

	gzf, err := gzip.NewReader(f)
	if err != nil {
		return err
	}

	return ExtractLayerTar(gzf, destination)
}
