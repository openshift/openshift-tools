#!/bin/bash -e

echo -n "Running zabbix server..."
sudo docker run -ti \
       --net=host \
       -p 10050:10050 \
       -p 10051:10051 \
       -v /var/lib/docker/volumes/shared:/shared:rw \
     oso-rhel7-zabbix-server $@
echo "Done."
