#!/bin/bash

# This script tests the high level end-to-end functionality

set -o errexit
set -o nounset
set -o pipefail

II_ROOT=$(dirname "${BASH_SOURCE}")/../..
source "${II_ROOT}/hack/util.sh"
source "${II_ROOT}/hack/cmd_util.sh"
ii::log::install_errexit

source "${II_ROOT}/hack/lib/util/environment.sh"
ii::util::environment::setup_time_vars

# test args
ii::cmd::expect_failure_and_text "image-inspector --help" "Usage of"
ii::cmd::expect_failure_and_text "image-inspector" "Error: docker image to inspect must be specified"
ii::cmd::expect_failure_and_text "image-inspector --image=fedora:22 --dockercfg=badfile" "badfile does not exist"
ii::cmd::expect_failure_and_text "image-inspector --image=fedora:22 --dockercfg=badfile --username=foo" "Error: only specify dockercfg file or username/password pair for authentication"
ii::cmd::expect_failure_and_text "image-inspector --image=fedora:22 --password-file=foo" "foo does not exist"
ii::cmd::expect_failure_and_text "image-inspector --image=fedora:22 --scan-type=foo" "foo is not one of the available scan-type"
ii::cmd::expect_failure_and_text "image-inspector --image=fedora:22 --pull-policy=foo" "foo is not one of the available pull-policy"
ii::cmd::expect_failure_and_text "image-inspector --image=fedora:22 --scan-type=foo" "Error: foo is not one of the available scan-types which are \[openscap clamav\]"


# test extraction
ii::cmd::expect_success_and_text "image-inspector --image=fedora:22 --scan-type=openscap 2>&1" "Extracting image fedora:22"

# TODO
# test serving
# test scanning valid and invalid params

