#!/bin/bash -e

RED="$(echo -e '\033[1;31m')"
NORM="$(echo -e '\033[0m')"

sudo echo -e "\nTesting sudo works...\n"

function is_rhel()
{
  grep -qi 'Red Hat Enterprise Linux' /etc/redhat-release
  return $?
}

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)


tmpfile=""

if ! is_rhel ; then
  tmpfile=$(mktemp Dockerfile-XXXXX)
  echo
  echo "Not rhel, enabling entitlement workaround:"
  echo
  echo "Downloading etc-pki-entitlement. ${RED}DO NOT CHECK THIS IN!!!${NORM}"
  scp -r tower.ops.rhcloud.com:/etc/pki/entitlement etc-pki-entitlement
  echo

  echo -n "Updating Dockerfile to include etc-pki-entitlement..."
  cp Dockerfile $tmpfile
  sed -i 's#FROM.*#&\nADD etc-pki-entitlement /run/secrets/etc-pki-entitlement#' Dockerfile
  echo "Done."
fi

# Build ourselves
echo
echo "Building oso-rhel7-ops-base..."
sudo time docker build $@ -t oso-rhel7-ops-base . && \
sudo docker tag -f oso-rhel7-ops-base docker-registry.ops.rhcloud.com/ops/oso-rhel7-ops-base

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
