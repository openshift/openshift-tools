package imageacquirer

import (
	"fmt"
	docker "github.com/fsouza/go-dockerclient"
	iiapi "github.com/openshift/image-inspector/pkg/api"
	"io"
	"testing"
)

func Test_decodeDockerResponse(t *testing.T) {
	no_error_input := "{\"Status\": \"fine\"}"
	one_error := "{\"Status\": \"fine\"}{\"Error\": \"Oops\"}{\"Status\": \"fine\"}"
	decode_error := "{}{}what"
	decode_error_message := "Error decoding json: invalid character 'w' looking for beginning of value"
	tests := map[string]struct {
		readerInput    string
		expectedErrors bool
		errorMessage   string
	}{
		"no error":      {readerInput: no_error_input, expectedErrors: false},
		"error":         {readerInput: one_error, expectedErrors: true, errorMessage: "Oops"},
		"decode errror": {readerInput: decode_error, expectedErrors: true, errorMessage: decode_error_message},
	}

	for test_name, test_params := range tests {
		parsedErrors := make(chan error, 100)
		finished := make(chan bool, 1)
		defer func() {
			<-finished // wait for decodeDockerResponse to finish
			close(finished)
			close(parsedErrors)
		}()

		go func() {
			reader, writer := io.Pipe()
			// handle closing the reader/writer in the method that creates them
			defer reader.Close()
			defer writer.Close()
			go decodeDockerResponse(parsedErrors, reader, finished)
			writer.Write([]byte(test_params.readerInput))
		}()

		select {
		case decodedErrors := <-parsedErrors:
			if decodedErrors == nil && test_params.expectedErrors {
				t.Errorf("Expected to parse an error, but non was parsed in test %s", test_name)
			}
			if decodedErrors != nil {
				if !test_params.expectedErrors {
					t.Errorf("Expected not to get errors in test %s but got: %v", test_name, decodedErrors)
				} else {
					if decodedErrors.Error() != test_params.errorMessage {
						t.Errorf("Expected error message is different than expected in test %s. Expected %v received %v",
							test_name, test_params.errorMessage, decodedErrors.Error())
					}
				}
			}
		}
	}
}

type mockDockerRuntimeClientFailAll struct{}

func (c mockDockerRuntimeClientFailAll) InspectImage(name string) (*docker.Image, error) {
	return nil, fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}
func (c mockDockerRuntimeClientFailAll) ContainerChanges(id string) ([]docker.Change, error) {
	return nil, fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}
func (c mockDockerRuntimeClientFailAll) PullImage(opts docker.PullImageOptions, auth docker.AuthConfiguration) error {
	return fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}
func (c mockDockerRuntimeClientFailAll) CreateContainer(opts docker.CreateContainerOptions) (*docker.Container, error) {
	return nil, fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}
func (c mockDockerRuntimeClientFailAll) RemoveContainer(opts docker.RemoveContainerOptions) error {
	return fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}
func (c mockDockerRuntimeClientFailAll) InspectContainer(id string) (*docker.Container, error) {
	return nil, fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}
func (c mockDockerRuntimeClientFailAll) DownloadFromContainer(id string, opts docker.DownloadFromContainerOptions) error {
	return fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}

type mockRuntimeClientPullSuccess struct {
	mockDockerRuntimeClientFailAll
}

func (c mockRuntimeClientPullSuccess) PullImage(opts docker.PullImageOptions, auth docker.AuthConfiguration) error {
	return nil
}

type mockRuntimeClientInspectSuccess struct {
	mockDockerRuntimeClientFailAll
}

func (c mockRuntimeClientInspectSuccess) InspectImage(name string) (*docker.Image, error) {
	return &docker.Image{}, nil
}

type mockDockerRuntimeClientAllSuccess struct{}

func (c mockDockerRuntimeClientAllSuccess) InspectImage(name string) (*docker.Image, error) {
	return &docker.Image{}, nil
}
func (c mockDockerRuntimeClientAllSuccess) ContainerChanges(id string) ([]docker.Change, error) {
	return []docker.Change{}, nil
}
func (c mockDockerRuntimeClientAllSuccess) PullImage(opts docker.PullImageOptions, auth docker.AuthConfiguration) error {
	return nil
}
func (c mockDockerRuntimeClientAllSuccess) CreateContainer(opts docker.CreateContainerOptions) (*docker.Container, error) {
	return &docker.Container{}, nil
}
func (c mockDockerRuntimeClientAllSuccess) RemoveContainer(opts docker.RemoveContainerOptions) error {
	return nil
}
func (c mockDockerRuntimeClientAllSuccess) InspectContainer(id string) (*docker.Container, error) {
	return &docker.Container{}, nil
}
func (c mockDockerRuntimeClientAllSuccess) DownloadFromContainer(id string, opts docker.DownloadFromContainerOptions) error {
	// forcefully send EOF
	opts.OutputStream.(*io.PipeWriter).Close()
	return nil
}

func TestPockerPullImage(t *testing.T) {
	for k, v := range map[string]struct {
		client      DockerRuntimeClient
		shouldFail  bool
		expectedErr string
	}{
		"With instant pull failing client": {shouldFail: true,
			client:      mockDockerRuntimeClientFailAll{},
			expectedErr: "Unable to pull docker image: mockDockerRuntimeClientFailAll FAIL"},
		"With instant pull success client": {shouldFail: false,
			client: mockRuntimeClientPullSuccess{}},
	} {
		dii := &dockerImageAcquirer{}
		err := dii.dockerPullImage("mockimage", v.client)
		if v.shouldFail {
			if err == nil {
				t.Errorf("%s should have failed but it didn't", k)
			} else {
				if err.Error() != v.expectedErr {
					t.Errorf("Wrong error message for %s.\nExpected: %s\nReceived: %s\n", k, v.expectedErr, err.Error())
				}
			}
		} else {
			if err != nil {
				t.Errorf("%s should not have failed with: %s", k, err.Error())
			}
		}
	}
}

func TestAcquireDockerImage(t *testing.T) {
	for k, v := range map[string]struct {
		client      DockerRuntimeClient
		pullPolicy  string
		shouldFail  bool
		expectedErr string
	}{
		"When unable to inspect image and also never pull": {
			shouldFail: true,
			client:     mockDockerRuntimeClientFailAll{},
			pullPolicy: iiapi.PullNever,
			expectedErr: fmt.Sprintf("Image %s is not available and pull-policy %s doesn't allow pulling",
				"mockimage", iiapi.PullNever)},
		"When unable to inspect or pull image and also always pull": {
			shouldFail:  true,
			client:      mockDockerRuntimeClientFailAll{},
			pullPolicy:  iiapi.PullAlways,
			expectedErr: "Unable to pull docker image: mockDockerRuntimeClientFailAll FAIL"},
		"When unable to inspect or pull image and also pull if no present": {
			shouldFail:  true,
			client:      mockDockerRuntimeClientFailAll{},
			pullPolicy:  iiapi.PullIfNotPresent,
			expectedErr: "Unable to pull docker image: mockDockerRuntimeClientFailAll FAIL"},
		"happy path sanity": {
			shouldFail: false,
			client:     mockDockerRuntimeClientAllSuccess{},
			pullPolicy: iiapi.PullAlways},
	} {
		dii := &dockerImageAcquirer{PreferedDestination: "/", PullPolicy: v.pullPolicy}
		_, _, _, _, err := dii.AcquireDockerImage("mockimage", v.client)
		if v.shouldFail {
			if err == nil {
				t.Errorf("%s should have failed but it didn't", k)
			} else {
				if err.Error() != v.expectedErr {
					t.Errorf("Wrong error message for %s.\nExpected: %s\nReceived: %s\n", k, v.expectedErr, err.Error())
				}
			}
		} else {
			if err != nil {
				t.Errorf("%s should not have failed with: %s", k, err.Error())
			}
		}
	}
}
