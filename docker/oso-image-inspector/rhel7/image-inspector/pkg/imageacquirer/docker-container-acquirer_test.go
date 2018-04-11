package imageacquirer

import (
	"fmt"
	docker "github.com/fsouza/go-dockerclient"
	"testing"
)

type mockRuntimeClientAllSuccessButContainerChanges struct {
	mockDockerRuntimeClientAllSuccess
}

func (c mockRuntimeClientAllSuccessButContainerChanges) ContainerChanges(id string) ([]docker.Change, error) {
	return []docker.Change{}, fmt.Errorf("mockDockerRuntimeClientFailAll FAIL")
}

func TestAcquireImageFromDockerContainer(t *testing.T) {
	for k, v := range map[string]struct {
		client      DockerRuntimeClient
		shouldFail  bool
		expectedErr string
	}{
		"Unable to inspect running container": {
			shouldFail:  true,
			client:      mockDockerRuntimeClientFailAll{},
			expectedErr: "Unable to get docker container information: mockDockerRuntimeClientFailAll FAIL"},
		"Cannot get container changes": {
			shouldFail:  true,
			client:      mockRuntimeClientAllSuccessButContainerChanges{},
			expectedErr: "Unable to get docker container changes: mockDockerRuntimeClientFailAll FAIL"},
		"Success with running Container": {
			shouldFail: false,
			client:     mockDockerRuntimeClientAllSuccess{}},
	} {
		dcia := &dockerContainerImageAcquirer{ScanContainerChanges: true}
		_, _, _, _, err := dcia.AcquireImageFromDockerContainer("mockcontainer", v.client)
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
