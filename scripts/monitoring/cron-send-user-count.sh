#!/bin/bash -e

COUNT=$(KUBECONFIG=/etc/openshift/master/admin.kubeconfig oc get --no-headers users | wc -l ; exit ${PIPESTATUS[0]})

echo
echo "Number of users : $COUNT"
echo
echo "Running: ops-zagg-client -k 'openshift.master.user.count' -o '$COUNT'"
ops-zagg-client -k "openshift.master.user.count" -o "$COUNT"
echo
