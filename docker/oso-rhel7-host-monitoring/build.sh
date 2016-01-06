#!/bin/bash

sudo echo -e "\nTesting sudo works...\n"

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)

## Make sure base is built with latest changes since we depend on it.
# commenting this out for now because ops-base does a full rebuild everytime
#if ../oso-rhel7-ops-base/build.sh ; then
  # Build ourselves
  echo
  echo "Building oso-rhel7-host-monitoring..."
  sudo time docker build $@ -t oso-rhel7-host-monitoring . && \
  sudo docker tag -f oso-rhel7-host-monitoring docker-registry.ops.rhcloud.com/ops/oso-rhel7-host-monitoring
#fi
