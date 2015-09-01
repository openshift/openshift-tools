#!/bin/bash

# Make sure pcp-base is pushed with the latest changes since we depend on it.
if ../pcp-base/push.sh ; then
  # Push ourselves
  echo
  echo "Pushing oso-rhel7-zagg-client..."
  sudo docker push docker-registry.ops.rhcloud.com/ops/oso-f22-host-monitoring
fi
