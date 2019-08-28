#!/bin/bash
# This script checks if dedicated-admin-operator is running, and send status to Zabbix.
# It also works with the legacy dedicated-admin script, so clusters that haven't been migrated
# to the operator yet will still have monitoring.

# The following error handlers are below:
# Exit on error, trace the error, exit when unbound variables are used.
set -o errexit
set -o errtrace
set -o nounset
trap 'echo "ERROR at line ${LINENO}"' ERR

function zabbix_ok {
  echo "Sending 'OK' to zabbix:"
  echo "ops-metric-client -k openshift.master.service.dedicated.admin.count -o 1"
  ops-metric-client -k openshift.master.service.dedicated.admin.count -o 1
}

function zabbix_not_ok {
  echo "Dedicated admin is not running on this host. Sending 'not OK' to zabbix:"
  echo "ops-metric-client -k openshift.master.service.dedicated.admin.count -o 0"
  ops-metric-client -k openshift.master.service.dedicated.admin.count -o 0
}

# Check the cluster tier to see if dedicated-admin should be running.
# Also, since OSD is comprised of `dedicated`, `rhmi` and potentially other tiers,
# use a blacklist here instead of a whitelist.
if [ $CLUSTERTIER == "pro" ] || [ $CLUSTERTIER == "osio" ] || [ $CLUSTERTIER == "ipaas" ]; then
  echo "Exiting because g_cluster_tier $CLUSTERTIER is excluded from dedicated-admin monitoring."
  zabbix_ok
  exit
fi

# Check the `ready` field of the dedicated-admin-operator pod.
echo "Checking for dedicated-admin-operator pod..."
pod_ready="$(oc --kubeconfig=/tmp/admin.kubeconfig get pods -n openshift-dedicated-admin -o=custom-columns=STATUS:.status.containerStatuses[*].ready --no-headers=true)"

if [ $pod_ready == "true" ]; then
  echo "Found dedicated-admin-operator pod in 'ready' state."
  zabbix_ok
else
  echo "Dedicated-admin-operator not found."
  echo "Checking for legacy dedicated-admin script..."
  echo -n "Number of processes running: "
  if pgrep -c -a -f /usr/bin/apply-dedicated-roles.py ; then
    echo "Found dedicated-admin process running."
    zabbix_ok
  else
    zabbix_not_ok
  fi
fi
