#!/bin/bash

#
# Edit this, then copy and "compress" using ctrl-j
#
# This config works against a local ZAIO
#
#{
#  "targets": [
#    {
#      "name": "local zaio",
#      "type": "zabbix",
#      "trapper_server": "oso-rhel7-zaio",
#      "trapper_port": 10051,
#      "api_url": "https://oso-rhel7-zaio/zabbix/api_jsonrpc.php",
#      "api_user": "Admin",
#      "api_password": "zabbix",
#      "ssl_verify": False,
#      "path": "/var/run/zagg/data/local_zaio",
#    },
#  ]
#}
#


export ZAGG_SERVER_CONFIG='{ "targets": [ { "name": "local zaio", "type": "zabbix", "trapper_server": "oso-rhel7-zaio", "trapper_port": 10051, "api_url": "https://oso-rhel7-zaio/zabbix/api_jsonrpc.php", "api_user": "Admin", "api_password": "zabbix", "ssl_verify": False, "path": "/var/run/zagg/data/local_zaio", }, ] }'

sudo echo -e "\nTesting sudo works...\n"

  #--net container:oso-rhel7-zaio \
sudo docker run -ti --rm --name oso-rhel7-zagg-web \
  --link oso-rhel7-zaio:oso-rhel7-zaio \
  -e "ZAGG_SERVER_CONFIG=$ZAGG_SERVER_CONFIG" \
  -e "ZAGG_SERVER_USER=admin" \
  -e "ZAGG_SERVER_PASSWORD=password" \
  -v /etc/localtime:/etc/localtime \
  -v /var/lib/docker/volumes/shared:/shared:rw \
  -p 8000:8000 \
  -p 8443:8443 \
  oso-rhel7-zagg-web $1
