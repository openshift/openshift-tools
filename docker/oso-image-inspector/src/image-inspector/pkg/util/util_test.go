package util

import (
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
