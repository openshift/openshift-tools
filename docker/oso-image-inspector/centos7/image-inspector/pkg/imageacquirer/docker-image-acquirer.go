package imageacquirer

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"time"

	docker "github.com/fsouza/go-dockerclient"
	iiapi "github.com/openshift/image-inspector/pkg/api"
	"github.com/openshift/image-inspector/pkg/util"
)

const (
	PULL_LOG_INTERVAL_SEC = 10 * time.Second
)

type dockerImageAcquirer struct {
	DockerSocket        string       // DockerSocket for the local docker daemon
	PreferedDestination string       // PreferedDestination for the extraction of the image
	PullPolicy          string       // PullPolicy controls whether we try to pull the inspected image
	Auths               AuthsOptions // Sources for authentications with docker
}

func (dii *dockerImageAcquirer) Acquire(source string) (string, docker.Image, iiapi.ScanResult, iiapi.FilesFilter, error) {
	client, err := docker.NewClient(dii.DockerSocket)
	if err != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil,
			fmt.Errorf("Unable to connect to docker daemon: %v", err)
	}
	return dii.AcquireDockerImage(source, client)
}

func (dii *dockerImageAcquirer) AcquireDockerImage(source string, client DockerRuntimeClient) (string, docker.Image, iiapi.ScanResult, iiapi.FilesFilter, error) {
	var err error
	imageMetaBefore, inspectErrBefore := client.InspectImage(source)
	if dii.PullPolicy == iiapi.PullNever && inspectErrBefore != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil,
			fmt.Errorf("Image %s is not available and pull-policy %s doesn't allow pulling",
				source, dii.PullPolicy)
	}

	if dii.PullPolicy == iiapi.PullAlways ||
		(dii.PullPolicy == iiapi.PullIfNotPresent && inspectErrBefore != nil) {
		if err = dii.dockerPullImage(source, client); err != nil {
			return "", docker.Image{}, iiapi.ScanResult{}, nil, err
		}
	}

	imageMetaAfter, inspectErrAfter := client.InspectImage(source)
	if inspectErrBefore == nil && inspectErrAfter == nil &&
		imageMetaBefore.ID == imageMetaAfter.ID {
		log.Printf("Image %s was already available", source)
	}

	imageMetadata, dstPath, err := dii.extractImageFromContainer(client, source)
	if err != nil {
		return "", docker.Image{}, iiapi.ScanResult{}, nil, err
	}

	scanResults := iiapi.ScanResult{
		APIVersion: iiapi.DefaultResultsAPIVersion,
		ImageName:  source,
		ImageID:    imageMetadata.ID,
		Results:    []iiapi.Result{},
	}
	return dstPath, *imageMetadata, scanResults, nil, nil
}

// dockerPullImage pulls the inspected image through the docker socket
// using the given client.
// It will try to use all detected authentication methods and will fail
// only if all of them failed.
func (dii *dockerImageAcquirer) dockerPullImage(source string, client DockerRuntimeClient) error {
	log.Printf("Pulling image %s", source)

	var imagePullAuths *docker.AuthConfigurations
	var authCfgErr error
	if imagePullAuths, authCfgErr = getAuthConfigs(dii.Auths); authCfgErr != nil {
		return authCfgErr
	}

	// Try all the possible auth's from the config file
	var err error
	for name, auth := range imagePullAuths.Configs {
		parsedErrors := make(chan error, 100)
		finished := make(chan bool, 1)

		defer func() {
			<-finished
			close(finished)
			close(parsedErrors)
		}()

		go func() {
			reader, writer := io.Pipe()
			defer writer.Close()
			defer reader.Close()
			imagePullOption := docker.PullImageOptions{
				Repository:    source,
				OutputStream:  writer,
				RawJSONStream: true,
			}
			go decodeDockerResponse(parsedErrors, reader, finished)

			if err = client.PullImage(imagePullOption, auth); err != nil {
				parsedErrors <- err
			}
		}()

		if parsedError := <-parsedErrors; parsedError != nil {
			log.Printf("Pulling image with authentication %s failed: %v", name, parsedError)
		} else {
			return nil
		}
	}
	return fmt.Errorf("Unable to pull docker image: %v", err)
}

// aggregateBytesAndReport sums the numbers recieved from its input channel
// bytesChan and prints them to the log every PULL_LOG_INTERVAL_SEC seconds.
// It will exit after bytesChan is closed.
func aggregateBytesAndReport(bytesChan chan int) {
	var bytesDownloaded int = 0
	ticker := time.NewTicker(PULL_LOG_INTERVAL_SEC)
	defer ticker.Stop()
	for {
		select {
		case bytes, open := <-bytesChan:
			if !open {
				log.Printf("Finished Downloading Image (%dKb downloaded)", bytesDownloaded/1024)
				return
			}
			bytesDownloaded += bytes
		case <-ticker.C:
			log.Printf("Downloading Image (%dKb downloaded)", bytesDownloaded/1024)
		}
	}
}

// decodeDockerResponse will parse the docker pull messages received
// from reader. It will start aggregateBytesAndReport with bytesChan
// and will push the difference of bytes downloaded to bytesChan.
// Errors encountered during parsing are reported to parsedErrors channel.
// After reader is closed it will send nil on parsedErrors, close bytesChan and send true on finished.
func decodeDockerResponse(parsedErrors chan error, reader io.Reader, finished chan bool) {
	type progressDetailType struct {
		Current, Total int
	}
	type pullMessage struct {
		Status, Id     string
		ProgressDetail progressDetailType
		Error          string
	}
	bytesChan := make(chan int, 100)
	defer func() { close(bytesChan) }()           // Closing the channel to end the other routine
	layersBytesDownloaded := make(map[string]int) // bytes downloaded per layer
	dec := json.NewDecoder(reader)                // decoder for the json messages

	var startedDownloading = false
	for {
		var v pullMessage
		if err := dec.Decode(&v); err != nil {
			if err != io.ErrClosedPipe && err != io.EOF {
				log.Printf("Error decoding json: %v", err)
				parsedErrors <- fmt.Errorf("Error decoding json: %v", err)
			} else {
				parsedErrors <- nil
			}
			break
		}
		// decoding
		if v.Error != "" {
			parsedErrors <- fmt.Errorf(v.Error)
			break
		}
		if v.Status == "Downloading" {
			if !startedDownloading {
				go aggregateBytesAndReport(bytesChan)
				startedDownloading = true
			}
			bytes := v.ProgressDetail.Current
			last, existed := layersBytesDownloaded[v.Id]
			if !existed {
				last = 0
			}
			layersBytesDownloaded[v.Id] = bytes
			bytesChan <- (bytes - last)
		}
	}

	finished <- true
}

// extractImageFromContainer creates a docker container based on the option's image with containerName.
// It will then insepct the container and image and then attempt to extract the image to
// option's destination path.  If the destination path is empty it will write to a temp directory
// and update the option's destination path with a /var/tmp directory.  /var/tmp is used to
// try and ensure it is a non-in-memory tmpfs.
func (dii *dockerImageAcquirer) extractImageFromContainer(client DockerRuntimeClient, source string) (*docker.Image, string, error) {
	var dstPath string

	containerName, err := generateRandomName()
	if err != nil {
		return nil, "", err
	}

	container, err := client.CreateContainer(docker.CreateContainerOptions{
		Name: containerName,
		Config: &docker.Config{
			Image: source,
			// For security purpose we don't define any entrypoint and command
			Entrypoint: []string{""},
			Cmd:        []string{""},
		},
	})
	if err != nil {
		return nil, "", fmt.Errorf("creating docker container: %v\n", err)
	}

	// delete the container when we are done extracting it
	defer func() {
		client.RemoveContainer(docker.RemoveContainerOptions{
			ID: container.ID,
		})
	}()

	containerMetadata, err := client.InspectContainer(container.ID)
	if err != nil {
		return nil, "", fmt.Errorf("getting docker container information: %v\n", err)
	}

	imageMetadata, err := client.InspectImage(containerMetadata.Image)
	if err != nil {
		return imageMetadata, "", fmt.Errorf("getting docker image information: %v\n", err)
	}

	if dstPath, err = util.CreateOutputDir(dii.PreferedDestination, "image-inspector-"); err != nil {
		return imageMetadata, "", fmt.Errorf("creating output dir: %v", err)
	}

	reader, writer := io.Pipe()
	// handle closing the reader/writer in the method that creates them
	defer writer.Close()
	defer reader.Close()

	log.Printf("Extracting image %s to %s", source, dstPath)

	// start the copy function first which will block after the first write while waiting for
	// the reader to read.
	errorChannel := make(chan error)
	go func() {
		errorChannel <- client.DownloadFromContainer(
			container.ID,
			docker.DownloadFromContainerOptions{
				OutputStream: writer,
				Path:         "/",
			})
	}()

	// block on handling the reads here so we ensure both the write and the reader are finished
	// (read waits until an EOF or error occurs).
	if err := ExtractLayerTar(reader, dstPath); err != nil {
		return nil, "", err
	}

	// capture any error from the copy, ensures both the handleTarStream and DownloadFromContainer
	// are done.
	err = <-errorChannel
	if err != nil {
		return imageMetadata, "", fmt.Errorf("extracting container: %v\n", err)
	}

	return imageMetadata, dstPath, nil
}
