#!/bin/bash -e

echo -n "Running oso-rhel7-zabbix-web... "
docker run -ti --net=host --rm=true --name zabbix-web oso-rhel7-zabbix-web
echo "Done.
