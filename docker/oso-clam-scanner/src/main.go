package main

import (
	"github.com/golang/glog"
	"github.com/openshift/clam-scanner/cmd"
)

func main() {
	if err := cmd.RootCmd.Execute(); err != nil {
		glog.Exitln(err)
	}
}
