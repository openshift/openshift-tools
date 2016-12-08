#!/bin/bash
# Loop checking every 5 minutes whether pmcd is working well

RESTART_CONTAINER="NULL"

while true
do
	sleep 30
    # Ensure that pmcd is running
    pgrep -f '/usr/libexec/pcp/bin/pmcd -A' &>/dev/null
	if [ $? -ne 0 ]; then
		RESTART_CONTAINER="RESTART"
	fi

    # Ensure that pminfo is getting valid data back
	pminfo -f kernel.uname.distro | grep "No PMCD"
	if [ $? -eq 0 ]; then
		RESTART_CONTAINER="RESTART"
	fi

    if [ "$RESTART_CONTAINER" = "RESTART" ]; then
        kill -9 $(cat /var/run/crond.pid)
    fi
done
