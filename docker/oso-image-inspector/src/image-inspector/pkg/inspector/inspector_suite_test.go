package inspector_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"

	"testing"
)

func TestInspector(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Inspector Suite")
}
