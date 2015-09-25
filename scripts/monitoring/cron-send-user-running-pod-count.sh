#!/bin/bash


COUNT=$(oadm manage-node --list-pods --selector=type=compute | grep Running | wc -l)
echo
echo "Number of User Running pod account : $COUNT"
echo
echo "Running: ops-zagg-client -k 'openshift.master.user.pod.running.count' -o '$COUNT'"
ops-zagg-client -k "openshift.master.user.pod.running.count" -o "$COUNT"
echo
