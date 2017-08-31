#!/bin/bash

cd $(dirname "$0")

OC=$(which oc)
if [ "$?" -ne "0" ]; then
	echo "Could not find 'oc' binary in path"
	exit 1
fi

echo "Stop host monitoring"
sudo docker stop oso-centos7-host-monitoring
sudo docker rm oso-centos7-host-monitoring
echo "Stop OpenShift"
sudo ${OC} cluster down

echo "Unloading temporary firewall changes"
sudo firewall-cmd --reload
