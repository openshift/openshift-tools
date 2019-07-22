#!/bin/bash
# This script checks if dedicated-admin-operator is running, and send status to Zabbix.

# The following error handlers are below:
# Exit on error, trace the error, exit when unbound variables are used.
set -o errexit
set -o errtrace
set -o nounset

# Check the `ready` field of the dedicated-admin-operator pod.
ready="$(oc --kubeconfig=/tmp/admin.kubeconfig get pods -n openshift-dedicated-admin -l k8s-app=dedicated-admin-operator \
  --template='{{ range .items }}{{ (index .status.containerStatuses 0).ready }}{{"\n"}}{{ end }}')"

if $ready; then
  echo "Detected pod in 'ready' state."
  oc --kubeconfig=/tmp/admin.kubeconfig get pods -n openshift-dedicated-admin -l k8s-app=dedicated-admin-operator 
  echo "Sending zabbix metric:"
  echo "ops-metric-client -k openshift.master.service.dedicated.admin.count -o 1"
  ops-metric-client -k openshift.master.service.dedicated.admin.count -o 1
else
  echo "Detected pod is NOT in 'ready' state."
  oc --kubeconfig=/tmp/admin.kubeconfig get pods -n openshift-dedicated-admin -l k8s-app=dedicated-admin-operator 
  echo "Sending zabbix metric:"
  echo "ops-metric-client -k openshift.master.service.dedicated.admin.count -o 0"
  ops-metric-client -k openshift.master.service.dedicated.admin.count -o 0
fi
