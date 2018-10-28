#!/bin/bash

# Make sure the script exits on first error
set -e

RED="$(echo -e '\033[1;31m')"
NORM="$(echo -e '\033[0m')"

function handle_err() {
  echo -e "\n${RED}ERROR: build script failed.${NORM}\n"
}

trap handle_err ERR


sudo echo -e "\nTesting if sudo works...\n"

cd $(dirname $0)

sudo time docker build $@ -t sre-openshift-provisioner .
