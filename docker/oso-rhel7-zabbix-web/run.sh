#!/bin/bash -e

echo -n "Running oso-rhel7-zabbix-web... "
docker run -ti --net=host --name web --rm=true oso-rhel7-zabbix-web
echo "Done.
