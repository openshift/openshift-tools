package util

import (
	"fmt"
	"io/ioutil"
	"os"
	"testing"
)

func TestStrOrDefault(t *testing.T) {
	if StrOrDefault("", "Default") != "Default" {
		t.Errorf("strOrDefault should return the default string if the first one is empty")
	}
	if StrOrDefault("TestString", "Default") != "TestString" {
		t.Errorf("strOrDefault should return the first string if it is not empty")
	}
}

func TestMin(t *testing.T) {
	if Min(2, 3) != 2 {
		t.Errorf("should return 2")
	}
	if Min(3, 2) != 2 {
		t.Errorf("should return 2")
	}
}

func TestStringInList(t *testing.T) {
	if !StringInList("one", []string{"three", "two", "one"}) {
		t.Errorf("should be in the list")
	}
	if StringInList("four", []string{"three", "two", "one"}) {
		t.Errorf("Is not found in the list")
	}
}

func mkSucc(string, os.FileMode) error {
	return nil
}

func mkFail(string, os.FileMode) error {
	return fmt.Errorf("MKFAIL")
}

func tempSucc(string, string) (string, error) {
	return "tempname", nil
}

func tempFail(string, string) (string, error) {
	return "", fmt.Errorf("TEMPFAIL!")
}

func TestCreateOutputDir(t *testing.T) {
	oldMkdir := osMkdir
	defer func() { osMkdir = oldMkdir }()

	oldTempdir := ioutil.TempDir
	defer func() { ioutilTempDir = oldTempdir }()

	for k, v := range map[string]struct {
		dirName    string
		shouldFail bool
		newMkdir   func(string, os.FileMode) error
		newTempDir func(string, string) (string, error)
	}{
		"good existing dir": {dirName: "/tmp", shouldFail: false, newMkdir: mkSucc},
		"good new dir":      {dirName: "delete_me", shouldFail: false, newMkdir: mkSucc},
		"good temporary":    {dirName: "", shouldFail: false, newMkdir: mkSucc, newTempDir: tempSucc},
		"cant create temp":  {dirName: "", shouldFail: true, newMkdir: mkSucc, newTempDir: tempFail},
		"mkdir fails":       {dirName: "delete_me", shouldFail: true, newMkdir: mkFail},
	} {
		osMkdir = v.newMkdir
		ioutilTempDir = v.newTempDir
		_, err := CreateOutputDir(v.dirName, "temp-name-")
		if v.shouldFail {
			if err == nil {
				t.Errorf("%s should have failed but it didn't!", k)
			}
		} else {
			if err != nil {
				t.Errorf("%s should have succeeded but failed with %v", k, err)
			}
		}
	}
}
