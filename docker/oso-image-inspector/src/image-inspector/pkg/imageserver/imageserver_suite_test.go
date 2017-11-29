package imageserver

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"

	"testing"
)

func TestImageserver(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Imageserver Suite")
}
