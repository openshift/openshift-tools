#!/bin/bash -e
COUNT_RUNNING=$(KUBECONFIG=/etc/openshift/master/admin.kubeconfig oadm manage-node --list-pods --selector=type=compute | grep Running | wc -l  ; exit ${PIPESTATUS[0]})
echo
echo "Number of User Running pod account : $COUNT_RUNNING"
echo
echo "Running: ops-zagg-client -k 'openshift.master.pod.running.count' -o '$COUNT_RUNNING'"
ops-zagg-client -k "openshift.master.pod.running.count" -o "$COUNT_RUNNING"
COUNT_TOTAL=$(KUBECONFIG=/etc/openshift/master/admin.kubeconfig oadm manage-node --list-pods --selector=type=compute | wc -l  ; exit ${PIPESTATUS[0]})
echo
echo "Number of User pod Total account : $COUNT_TOTAL"
echo
echo "Running: ops-zagg-client -k 'openshift.master.pod.total.count' -o '$COUNT_TOTAL'"
ops-zagg-client -k "openshift.master.pod.total.count" -o "$COUNT_TOTAL"
echo 


