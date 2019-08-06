#!/bin/bash

if ! grep -qi 'Red Hat Enterprise Linux' /etc/redhat-release ; then
  echo "ERROR: We only allow pushing from a RHEL machine because it allows secrets volumes."
  exit 1
fi

echo
echo "Pushing oso-rhel7-ops-base..."
sudo docker push registry.reg-aws.openshift.com:443/ops/oso-rhel7-ops-base
