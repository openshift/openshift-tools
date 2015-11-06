#!/bin/bash
# Loop checking every 5 minutes whether pmcd is working well

while true
do
	sleep 300
	pminfo -f kernel.uname.distro | grep "No PMCD"

	if [ $? -eq 0 ]; then
		PID=$(pgrep -f "/usr/libexec/pcp/bin/pmpause")
		kill -9 $PID
	fi
done
