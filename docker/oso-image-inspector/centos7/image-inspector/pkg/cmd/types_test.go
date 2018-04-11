package cmd

import (
	"strings"
	"testing"
)

func TestValidate(t *testing.T) {
	noDockerSocket := NewDefaultImageInspectorOptions()
	noDockerSocket.UseDockerSocket = true
	noDockerSocket.DockerSocket = ""

	dockerCfgAndUsername := NewDefaultImageInspectorOptions()
	dockerCfgAndUsername.Image = "image"
	dockerCfgAndUsername.DockerCfg.Set("foo")
	dockerCfgAndUsername.Username = "bar"

	usernameNoPasswordFile := NewDefaultImageInspectorOptions()
	usernameNoPasswordFile.Image = "image"
	usernameNoPasswordFile.Username = "foo"

	noServeAndChroot := NewDefaultImageInspectorOptions()
	noServeAndChroot.Image = "image"
	noServeAndChroot.Chroot = true

	goodConfigUsername := NewDefaultImageInspectorOptions()
	goodConfigUsername.Image = "image"
	goodConfigUsername.Username = "username"
	goodConfigUsername.PasswordFile = "types.go"
	goodConfigUsername.ScanType = "clamav"
	goodConfigUsername.ClamSocket = "clamav"

	goodConfigWithDockerCfg := NewDefaultImageInspectorOptions()
	goodConfigWithDockerCfg.Image = "image"
	goodConfigWithDockerCfg.DockerCfg.Set("types.go")
	goodConfigWithDockerCfg.ScanType = "openscap"

	noScanTypeAndDir := NewDefaultImageInspectorOptions()
	noScanTypeAndDir.Image = "image"
	noScanTypeAndDir.ScanResultsDir = "/tmp"

	goodScanOptions := NewDefaultImageInspectorOptions()
	goodScanOptions.Image = "image"
	goodScanOptions.ScanType = "openscap"
	goodScanOptions.ScanResultsDir = "."
	goodScanOptions.OpenScapHTML = true

	notADirResScan := NewDefaultImageInspectorOptions()
	notADirResScan.Image = "image"
	notADirResScan.ScanType = "openscap"
	notADirResScan.ScanResultsDir = "types_test.go"

	noSuchScanType := NewDefaultImageInspectorOptions()
	noSuchScanType.Image = "image"
	noSuchScanType.ScanType = "nosuchscantype"
	noSuchScanType.ScanResultsDir = "."

	noSuchFileDockercfg := NewDefaultImageInspectorOptions()
	noSuchFileDockercfg.Image = "image"
	noSuchFileDockercfg.DockerCfg.Set("nosuchfile")

	badScanOptionsHTMLnoScan := NewDefaultImageInspectorOptions()
	badScanOptionsHTMLnoScan.Image = "image"
	badScanOptionsHTMLnoScan.OpenScapHTML = true

	badScanOptionsHTMLWrongScan := NewDefaultImageInspectorOptions()
	badScanOptionsHTMLWrongScan.Image = "image"
	badScanOptionsHTMLWrongScan.OpenScapHTML = true
	badScanOptionsHTMLWrongScan.ScanType = "nosuchscantype"

	noSuchPullPolicy := NewDefaultImageInspectorOptions()
	noSuchPullPolicy.Image = "image"
	noSuchPullPolicy.PullPolicy = "whatisdocker?"

	conflictOptions := NewDefaultImageInspectorOptions()
	conflictOptions.Image = "image"
	conflictOptions.Container = "container"

	tests := map[string]struct {
		inspector      *ImageInspectorOptions
		shouldValidate bool
	}{
		"no docker-socket":                    {inspector: noDockerSocket, shouldValidate: false},
		"no image":                            {inspector: NewDefaultImageInspectorOptions(), shouldValidate: false},
		"docker config and username":          {inspector: dockerCfgAndUsername, shouldValidate: false},
		"username and no password file":       {inspector: usernameNoPasswordFile, shouldValidate: false},
		"no serve and chroot":                 {inspector: noServeAndChroot, shouldValidate: false},
		"good config with username":           {inspector: goodConfigUsername, shouldValidate: true},
		"good config with docker cfg":         {inspector: goodConfigWithDockerCfg, shouldValidate: true},
		"no scan-type with scan-dir":          {inspector: noScanTypeAndDir, shouldValidate: false},
		"no such file dockercfg":              {inspector: noSuchFileDockercfg, shouldValidate: false},
		"no such scan type available":         {inspector: noSuchScanType, shouldValidate: false},
		"file exists and is not a dir":        {inspector: notADirResScan, shouldValidate: false},
		"good config with scan options":       {inspector: goodScanOptions, shouldValidate: true},
		"bad config with html and no scan":    {inspector: badScanOptionsHTMLnoScan, shouldValidate: false},
		"bad config with html and wrong scan": {inspector: badScanOptionsHTMLWrongScan, shouldValidate: false},
		"no such pull policy available":       {inspector: noSuchPullPolicy, shouldValidate: false},
		"conflict options":                    {inspector: conflictOptions, shouldValidate: false},
	}

	for k, v := range tests {
		err := v.inspector.Validate()

		if v.shouldValidate && err != nil {
			t.Errorf("%s expected to validate but received %v", k, err)
		}
		if !v.shouldValidate && err == nil {
			t.Errorf("%s expected to be invalid but received no error", k)
		}
	}

	// for 100% coverage we need to test MultiStringVar::String
	goodConfigWithDockerCfg.DockerCfg.Set("types_test.go")
	if len(goodConfigWithDockerCfg.DockerCfg.Values) != 2 {
		t.Errorf("MultiStringVar Set didn't add to the lenght of Values")
	}
	st := goodConfigWithDockerCfg.DockerCfg.String()
	if !strings.Contains(st, "types.go") || !strings.Contains(st, "types_test.go") {
		t.Errorf("MultiStringVar Set didn't add to the right values or Strings didn't return them")
	}
}
