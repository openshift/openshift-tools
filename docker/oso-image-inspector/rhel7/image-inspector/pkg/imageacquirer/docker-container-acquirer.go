package imageacquirer

import (
	"fmt"
	"os"
	"strings"

	docker "github.com/fsouza/go-dockerclient"
	iiapi "github.com/openshift/image-inspector/pkg/api"
)

type containerMeta struct {
	Container *docker.Container
	Image     *docker.Image
}

type dockerContainerImageAcquirer struct {
	DockerSocket         string // DockerSocket for the local docker daemon
	ScanContainerChanges bool   // ScanContainerChanges controls whether or not whole rootfs will be scanned.
}

func (dcia *dockerContainerImageAcquirer) Acquire(source string) (
	string, docker.Image, iiapi.ScanResult, iiapi.FilesFilter, error) {
	client, err := docker.NewClient(dcia.DockerSocket)
	if err != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil,
			fmt.Errorf("Unable to connect to docker daemon: %v\n", err)
	}
	return dcia.AcquireImageFromDockerContainer(source, client)
}

func (dcia *dockerContainerImageAcquirer) AcquireImageFromDockerContainer(source string,
	client DockerRuntimeClient) (
	string, docker.Image, iiapi.ScanResult, iiapi.FilesFilter, error) {
	meta, err := getContainerMeta(source, client)
	if err != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil, err
	}

	var filterInclude map[string]struct{}

	dstPath := fmt.Sprintf("/host/proc/%d/root/", meta.Container.State.Pid)

	if dcia.ScanContainerChanges {
		filterInclude, err = getContainerChanges(client, meta, source, dstPath)
		if err != nil {
			return "", docker.Image{}, iiapi.ScanResult{}, nil, err
		}
	}

	excludePrefixes := []string{
		dstPath + "proc",
		dstPath + "sys",
	}

	filterFn := func(path string, fileInfo os.FileInfo) bool {
		if filterInclude != nil {
			if _, ok := filterInclude[path]; !ok {
				return false
			}
		}

		for _, prefix := range excludePrefixes {
			if strings.HasPrefix(path, prefix) {
				return false
			}
		}

		return true
	}

	scanResults := iiapi.ScanResult{
		APIVersion:  iiapi.DefaultResultsAPIVersion,
		ImageID:     meta.Image.ID,
		ContainerID: source,
		Results:     []iiapi.Result{},
	}
	return dstPath, *meta.Image, scanResults, filterFn, nil
}

func getContainerMeta(source string, client DockerRuntimeClient) (
	*containerMeta, error) {
	var err error
	result := &containerMeta{}

	result.Container, err = client.InspectContainer(source)
	if err != nil {
		return nil, fmt.Errorf("Unable to get docker container information: %v", err)
	}

	result.Image, err = client.InspectImage(result.Container.Image)
	if err != nil {
		return nil, fmt.Errorf("Unable to get docker image information: %v", err)
	}

	return result, nil
}

func getContainerChanges(client DockerRuntimeClient, meta *containerMeta, source string, dstPath string) (map[string]struct{}, error) {
	containerChanges, err := client.ContainerChanges(source)
	if err != nil {
		return nil, fmt.Errorf("Unable to get docker container changes: %v", err)
	}

	// We don't want to scan anything if the containerChanges is empty.
	filter := make(map[string]struct{})

	for _, change := range containerChanges {
		switch change.Kind {
		case docker.ChangeAdd, docker.ChangeModify:
			filter[dstPath+change.Path] = struct{}{}
		}
	}

	return filter, nil
}
