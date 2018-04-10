package inspector

import (
	"testing"

	iicmd "github.com/openshift/image-inspector/pkg/cmd"
)

func TestAcquiringInInspect(t *testing.T) {
	for k, v := range map[string]struct {
		opts           iicmd.ImageInspectorOptions
		shouldFail     bool
		expectedAcqErr string
	}{
		"Invalid docker daemon endpoint": {
			opts:           iicmd.ImageInspectorOptions{DockerSocket: "No such file", UseDockerSocket: true},
			shouldFail:     true,
			expectedAcqErr: "Unable to connect to docker daemon: invalid endpoint",
		},
		"unknown containers lib transport": {
			opts: iicmd.ImageInspectorOptions{
				Image:           "transport-not-existing://imagename",
				UseDockerSocket: false,
			},
			shouldFail:     true,
			expectedAcqErr: "invalid source name docker://transport-not-existing://imagename: Invalid image name \"transport-not-existing://imagename\", unknown transport \"transport-not-existing\"",
		},
	} {
		ii := NewDefaultImageInspector(v.opts).(*defaultImageInspector)
		err := ii.Inspect()
		if v.shouldFail && err == nil {
			t.Errorf("%s should have failed but it didn't!", k)
		}
		if !v.shouldFail {
			if err != nil {
				t.Errorf("%s should have succeeded but failed with %v", k, err)
			}
		}
		if ii.meta.ImageAcquireError != v.expectedAcqErr {
			t.Errorf("%s acquire error is not matching.\nExtected: %v\nReceived: %v\n", k, v.expectedAcqErr, ii.meta.ImageAcquireError)
		}
	}
}
