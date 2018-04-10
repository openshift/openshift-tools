package imageacquirer

import (
	"archive/tar"
	"crypto/rand"
	"fmt"
	docker "github.com/fsouza/go-dockerclient"
	"io"
	"io/ioutil"
	"log"
	"math"
	"math/big"
	"os"
	"path"
	"path/filepath"
	"strings"
)

const (
	dockerTarPrefix = "rootfs/"
	ownerPermRW     = 0600

	opaqueWhiteoutFilename = ".wh..wh..opq"
	whiteoutFilePrefix     = ".wh"
)

func generateRandomName() (string, error) {
	n, err := rand.Int(rand.Reader, big.NewInt(math.MaxInt64))
	if err != nil {
		return "", fmt.Errorf("generating random container name: %v\n", err)
	}
	return fmt.Sprintf("image-inspector-%016x", n), nil
}

func appendDockerCfgConfigs(dockercfg string, cfgs *docker.AuthConfigurations) error {
	var imagePullAuths *docker.AuthConfigurations
	reader, err := os.Open(dockercfg)
	if err != nil {
		return fmt.Errorf("opening docker config file: %v\n", err)
	}
	defer reader.Close()
	if imagePullAuths, err = docker.NewAuthConfigurations(reader); err != nil {
		return fmt.Errorf("parsing docker config file: %v\n", err)
	}
	if len(imagePullAuths.Configs) == 0 {
		return fmt.Errorf("No auths were found in the given dockercfg file\n")
	}
	for name, ac := range imagePullAuths.Configs {
		cfgs.Configs[fmt.Sprintf("%s/%s", dockercfg, name)] = ac
	}
	return nil
}

func getAuthConfigs(opts AuthsOptions) (*docker.AuthConfigurations, error) {
	imagePullAuths := &docker.AuthConfigurations{Configs: map[string]docker.AuthConfiguration{"Default Empty Authentication": {}}}
	if len(opts.DockerCfg.Values) > 0 {
		for _, dcfgFile := range opts.DockerCfg.Values {
			if err := appendDockerCfgConfigs(dcfgFile, imagePullAuths); err != nil {
				log.Printf("WARNING: Unable to read docker configuration from %s. Error: %v", dcfgFile, err)
			}
		}
	}

	if opts.Username != "" {
		token, err := ioutil.ReadFile(opts.PasswordFile)
		if err != nil {
			return nil, fmt.Errorf("unable to read password file: %v\n", err)
		}
		imagePullAuths = &docker.AuthConfigurations{Configs: map[string]docker.AuthConfiguration{"": {Username: opts.Username, Password: string(token)}}}
	}

	return imagePullAuths, nil
}

func ExtractLayerTar(src io.Reader, destination string) error {
	tr := tar.NewReader(src)
	for {
		hdr, err := tr.Next()
		if err != nil {
			if err == io.EOF {
				return nil
			}
			return fmt.Errorf("Unable to read tar: %v\n", err)
		}

		hdrInfo := hdr.FileInfo()

		dstpath := path.Join(destination, strings.TrimPrefix(hdr.Name, dockerTarPrefix))
		// Overriding permissions to allow writing content
		mode := hdrInfo.Mode() | ownerPermRW

		// opaque whiteout file
		// https://github.com/opencontainers/image-spec/blob/master/layer.md#opaque-whiteout
		if strings.HasSuffix(dstpath, opaqueWhiteoutFilename) {
			dirToClear := filepath.Dir(dstpath)
			filepath.Walk(dirToClear, func(path string, info os.FileInfo, err error) error {
				if err != nil {
					return err
				}
				if path == dirToClear {
					return nil
				}
				return os.RemoveAll(path)
			})
			continue
		}
		// single whiteout file
		if strings.HasPrefix(filepath.Base(dstpath), whiteoutFilePrefix) {
			os.RemoveAll(dstpath)
			continue
		}

		switch hdr.Typeflag {
		case tar.TypeDir:
			if err := os.Mkdir(dstpath, mode); err != nil {
				if !os.IsExist(err) {
					return fmt.Errorf("Unable to create directory: %v", err)
				}
				err = os.Chmod(dstpath, mode)
				if err != nil {
					return fmt.Errorf("Unable to update directory mode: %v", err)
				}
			}
		case tar.TypeReg, tar.TypeRegA:
			file, err := os.OpenFile(dstpath, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, mode)
			if err != nil {
				return fmt.Errorf("Unable to create file: %v", err)
			}
			if _, err := io.Copy(file, tr); err != nil {
				file.Close()
				return fmt.Errorf("Unable to write into file: %v", err)
			}
			file.Close()
		case tar.TypeSymlink:
			if err := os.Symlink(hdr.Linkname, dstpath); err != nil {
				if os.IsExist(err) {
					continue
				}
				return fmt.Errorf("Unable to create symlink: %v\n", err)
			}
		case tar.TypeLink:
			target := path.Join(destination, strings.TrimPrefix(hdr.Linkname, dockerTarPrefix))
			if err := os.Link(target, dstpath); err != nil {
				if os.IsExist(err) {
					continue
				}
				return fmt.Errorf("Unable to create link: %v\n", err)
			}
		}

		// maintaining access and modification time in best effort fashion
		os.Chtimes(dstpath, hdr.AccessTime, hdr.ModTime)
	}
}
