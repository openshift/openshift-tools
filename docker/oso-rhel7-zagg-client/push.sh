#!/bin/bash

if ! grep -qi 'Red Hat Enterprise Linux' /etc/redhat-release ; then
  echo "ERROR: We only allow pushing from a RHEL machine because it allows secrets volumes."
  exit 1
fi

# Make sure base is pushed with the latest changes since we depend on it.
if ../oso-rhel7-ops-base/push.sh ; then
  # Push ourselves
  echo
  echo "Pushing oso-rhel7-zagg-client..."
  sudo docker push docker-registry.ops.rhcloud.com/ops/oso-rhel7-zagg-client
fi
