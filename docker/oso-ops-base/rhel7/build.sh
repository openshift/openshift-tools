#!/bin/bash

# Make sure the script exits on first error
set -e

RED="$(echo -e '\033[1;31m')"
NORM="$(echo -e '\033[0m')"

function handle_err() {
  echo -e "\n${RED}ERROR: build script failed.${NORM}\n"
}

trap handle_err ERR


sudo echo -e "\nTesting sudo works...\n"

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)

function is_rhel()
{
  grep -qi 'Red Hat Enterprise Linux' /etc/redhat-release
  return $?
}

tmpfile=""

if ! is_rhel ; then
    tmpfile=$(mktemp Dockerfile-XXXXX)
    echo
    echo "Not rhel, enabling entitlement workaround:"
    echo
    echo "Downloading etc-pki-entitlement. ${RED}DO NOT CHECK THIS IN!!!${NORM}"
    scp -r bastion-nasa-1.ops.openshift.com:/etc/pki/entitlement etc-pki-entitlement
    echo

    echo -n "Updating Dockerfile to include etc-pki-entitlement..."
    cp Dockerfile $tmpfile
    sed -i 's#FROM.*#&\nADD etc-pki-entitlement /etc-pki-entitlement#' Dockerfile
    echo "Done."
fi

# Build ourselves
echo
echo "Building oso-rhel7-ops-base..."
sudo time docker build $@ -t oso-rhel7-ops-base .
sudo docker tag oso-rhel7-ops-base registry.reg-aws.openshift.com:443/ops/oso-rhel7-ops-base

if ! is_rhel ; then
  echo
  echo "Not rhel, disabling entitlement workaround:"
  echo -n "Restoring original Dockerfile... "
  mv $tmpfile Dockerfile
  echo "Done."

  echo -n "Removing downloaded etc-pki-entitlement directory... "
  rm -rf etc-pki-entitlement
  echo "Done."
  echo
fi
