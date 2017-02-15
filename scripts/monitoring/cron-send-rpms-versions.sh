#!/bin/bash

# Check OpenShift version
OC_VERSION=$(oc version | sed -n '1{p;q}' | sed 's/[^0-9.]*\([0-9.]*\).*/\1/')

# Check Docker version
DOCKER_VERSION=$(docker --version | sed 's/[^0-9.]*\([0-9.]*\).*/\1/')

HOSTNAME=hostname --fqdn

# Send results to zabbix
ops-metrics-client -k "machine/$HOSTNAME/docker.version" -o "$DOCKER_VERSION"
ops-metrics-client -k "machine/$HOSTNAME/oc.version" -o "$OC_VERSION"
