#!/bin/bash

# The root of the build/dist directory
readonly II_ROOT=$(
  unset CDPATH
  ii_root=$(dirname "${BASH_SOURCE}")/..

  cd "${ii_root}"
  ii_root=`pwd`
  if [ -h "${ii_root}" ]; then
    readlink "${ii_root}"
  else
    pwd
  fi
)

readonly II_GOPATH=$(
  unset CDPATH
  cd ${II_ROOT}/../../../..
  pwd
)

readonly II_GO_PACKAGE=github.com/openshift/image-inspector
readonly II_OUTPUT_SUBPATH="${II_OUTPUT_SUBPATH:-_output/local}"
readonly II_OUTPUT="${II_ROOT}/${II_OUTPUT_SUBPATH}"
readonly II_OUTPUT_BINPATH="${II_OUTPUT}/bin"

# ii::build::setup_env will check that the `go` commands is available in
# ${PATH}. If not running on Travis, it will also check that the Go version is
# good enough for the webdav code requirements (1.5+).
#
# Output Vars:
#   export GOPATH - A modified GOPATH to our created tree along with extra
#     stuff.
#   export GOBIN - This is actively unset if already set as we want binaries
#     placed in a predictable place.
ii::build::setup_env() {
  if [[ -z "$(which go)" ]]; then
    cat <<EOF

Can't find 'go' in PATH, please fix and retry.
See http://golang.org/doc/install for installation instructions.

EOF
    exit 2
  fi

  # Travis continuous build uses a head go release that doesn't report
  # a version number, so we skip this check on Travis.  It's unnecessary
  # there anyway.
  if [[ "${TRAVIS:-}" != "true" ]]; then
    local go_version
    go_version=($(go version))
    if [[ "${go_version[2]}" < "go1.5" ]]; then
      cat <<EOF

Detected Go version: ${go_version[*]}.
image-inspector builds require Go version 1.5 or greater.

EOF
      exit 2
    fi
  fi

  unset GOBIN

  export GOPATH=${II_GOPATH}
  export II_TARGET_BIN=${II_GOPATH}/bin
}

# Build image-inspector.go binary.
ii::build::build_binaries() {
  # Create a sub-shell so that we don't pollute the outer environment
  (
    # Check for `go` binary and set ${GOPATH}.
    ii::build::setup_env

    # Making this super simple for now.
    local platform="local"
    export GOBIN="${II_OUTPUT_BINPATH}/${platform}"

    mkdir -p "${II_OUTPUT_BINPATH}/${platform}"
    go install "cmd/image-inspector.go"
  )
}
