#!/bin/bash

# 0: problem
# 1: all is well
PING_RETURN=1

# Check whether pcp appears to be alive and well
pminfo -f kernel.uname.sysname | grep -i "linux"

if [ $? -ne 0 ] ; then
	echo "pcp reporting bogus data"
	PING_RETURN=0
fi

# Send results to zabbix
ops-metric-client -k "pcp.ping" -o "$PING_RETURN"
