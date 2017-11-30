#!/bin/bash

set -e

STARTTIME=$(date +%s)
CODE_ROOT=$(dirname "${BASH_SOURCE}")/..
source "${CODE_ROOT}/hack/common.sh"
echo "Detected go version: $(go version)"

go get github.com/tools/godep
go get github.com/onsi/ginkgo/ginkgo  # installs the ginkgo CLI
go get github.com/onsi/gomega         # fetches the matcher library

ret=$?; ENDTIME=$(date +%s); echo "$0 took $(($ENDTIME - $STARTTIME)) seconds"; exit "$ret"
