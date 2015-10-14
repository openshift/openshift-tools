#!/bin/bash
# setting up the certificate and the key
CERT=`ls /etc/openshift/node/system*node*.crt`
KEY=`ls /etc/openshift/node/system*node*.key`

# querying the health ping
wget -q -O- --no-check-certificate --certificate=${CERT} --private-key=${KEY} https://0.0.0.0:10250/healthz/ping |grep -c "ok" >/dev/null
STATUS=$?

echo "Health ping returned ${STATUS}"
echo
echo "Running: ops-zagg-client -k 'openshift.node.etcd.ping' -o '$STATUS'"
ops-zagg-client -k "openshift.node.etcd.ping" -o "$STATUS"
