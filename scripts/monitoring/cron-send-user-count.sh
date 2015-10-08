#!/bin/bash

COUNT=$(oca get --no-headers users | wc -l)
echo
echo "Number of users : $COUNT"
echo
echo "Running: ops-zagg-client -k 'openshift.master.user.count' -o '$COUNT'"
ops-zagg-client -k "openshift.master.user.count" -o "$COUNT"
echo
