#!/bin/bash -e

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)

# Build ourselves
echo
echo "Building oso-rhel7-ops-base..."
time docker build $@ -t oso-rhel7-ops-base .
docker tag -f oso-rhel7-ops-base docker-registry.ops.rhcloud.com/ops/oso-rhel7-ops-base
