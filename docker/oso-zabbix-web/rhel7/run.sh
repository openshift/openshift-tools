#!/bin/bash -e

echo -n "Running oso-rhel7-zabbix-web... "
sudo docker run -ti --net=host --rm=true -e 'ZABBIX_SERVER_HOSTNAME=oso-rhel7-zabbix-server' --name zabbix-web oso-rhel7-zabbix-web $@
echo "Done."
