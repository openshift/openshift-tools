#!/bin/bash
# Loop checking whether socket is available

TESTLOCATION=/var/run/openvswitch/db.sock

while true
do
    sleep 600

    if [ ! -S ${TESTLOCATION} ]; then
        echo "${0} : ${TESTLOCATION} does not exist!"
        /root/kill-container.sh
    fi
done
