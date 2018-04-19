#!/bin/bash
CAP=-1

CAPACITY=$(/host/bin/cluster-capacity --kubeconfig /tmp/admin.kubeconfig --podspec /etc/openshift_tools/podspec.yaml)

re="^[0-9]+$"
if [[ $CAPACITY =~ $re ]]; then
  CAP=$CAPACITY
fi

/usr/bin/ops-metric-client -k openshift.cluster.capacity -o $CAP --synthetic
