#!/bin/bash -e


COUNT=$(KUBECONFIG=/etc/openshift/master/admin.kubeconfig oadm manage-node --list-pods --selector=type=compute | grep Running | wc -l  ; exit ${PIPESTATUS[0]})
echo
echo "Number of User Running pod account : $COUNT"
echo
echo "Running: ops-zagg-client -k 'openshift.master.user.pod.running.count' -o '$COUNT'"
ops-zagg-client -k "openshift.master.user.pod.running.count" -o "$COUNT"
echo
