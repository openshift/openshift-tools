#!/bin/bash -e

COUNT=$(KUBECONFIG=/etc/openshift/master/admin.kubeconfig oc get --no-headers users | wc -l)
if [ ${PIPESTATUS[0]} -ne 0 ] ; then
  echo "Error: oc command failed"
  exit 5
fi

echo
echo "Number of users : $COUNT"
echo
echo "Running: ops-zagg-client -k 'openshift.master.user.count' -o '$COUNT'"
ops-zagg-client -k "openshift.master.user.count" -o "$COUNT"
echo
