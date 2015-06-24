#!/bin/bash -e

echo -n "Running zabbix server..."
docker run -ti --net=host -p 10050:10050 -p 10051:10051 oso-rhel7-zabbix-server $@
echo "Done."
