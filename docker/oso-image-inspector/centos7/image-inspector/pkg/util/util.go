package util

import (
	"fmt"
	"io/ioutil"
	"os"
)

var osMkdir = os.Mkdir
var ioutilTempDir = ioutil.TempDir

// StrOrDefault returns the string s or d if s is empty
func StrOrDefault(s string, d string) string {
	if len(s) == 0 { // s || d
		return d
	}
	return s
}

// Min returns the minimum value of x and y
func Min(x, y int) int {
	if x < y {
		return x
	}
	return y
}

// StringInList Return true iff the string s is found in the string array l
func StringInList(s string, l []string) bool {
	for _, opt := range l {
		if s == opt {
			return true
		}
	}
	return false
}

// CreateOutputDir will try to create a directory in the path dirName unless it exists.
// if dirName is empty it will try to create a directory with the name tempName in /var/tmp
// the return value string is the name of the created direcory (or its name if it already existed)
func CreateOutputDir(dirName string, tempName string) (string, error) {
	if len(dirName) > 0 {
		err := osMkdir(dirName, 0755)
		if err != nil {
			if !os.IsExist(err) {
				return "", fmt.Errorf("creating destination path: %v\n", err)
			}
		}
	} else {
		// forcing to use /var/tmp because often it's not an in-memory tmpfs
		var err error
		dirName, err = ioutilTempDir("/var/tmp", tempName)
		if err != nil {
			return "", fmt.Errorf("creating temporary path: %v\n", err)
		}
	}
	return dirName, nil
}
