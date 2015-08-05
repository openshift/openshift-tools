#!/bin/bash


# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)

# Make sure base is built with latest changes since we depend on it.
if ../oso-rhel7-ops-base/build.sh ; then
  # Build ourselves
  echo
  echo "Building oso-rhel7-mysql..."
  time docker build $@ -t oso-rhel7-mysql .
fi
