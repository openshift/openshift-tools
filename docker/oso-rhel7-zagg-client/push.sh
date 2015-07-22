#!/bin/bash

# Make sure base is pushed with the latest changes since we depend on it.
../oso-rhel7-ops-base/build.sh

# Push ourselves
echo
echo "Pushing oso-rhel7-zagg-client..."
docker push docker-registry.ops.rhcloud.com/ops/oso-rhel7-zagg-client
