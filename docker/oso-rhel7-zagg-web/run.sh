#!/bin/bash

#
# Edit this, then copy and "compress" using ctrl-j
#
# This config works against a local ZAIO
#
#{
#  "targets": [
#    {
#      "name": "local cluster zabbix server",
#      "type": "zabbix",
#      "trapper_server": "localhost",
#      "trapper_port": 10051,
#      "api_url": "http://localhost/zabbix/api_jsonrpc.php",
#      "api_user": "Admin",
#      "api_password": "zabbix",
#      "path": "/var/run/zagg/data/local_cluster_zbx",
#    },
#    {
#      "name": "remote zagg",
#      "type": "zagg",
#      "host": "localhost:8000",
#      "user": "admin",
#      "password": "password",
#      "path": "/var/run/zagg/data/remote_zagg",
#    }
#  ]
#}
#


export ZAGG_SERVER_CONFIG='{ "targets": [ { "name": "local cluster zabbix server", "type": "zabbix", "trapper_server": "localhost", "trapper_port": 10051, "api_url": "http://localhost/zabbix/api_jsonrpc.php", "api_user": "Admin", "api_password": "zabbix", "path": "/var/run/zagg/data/local_cluster_zbx", }, { "name": "remote zagg", "type": "zagg", "host": "localhost:8000", "user": "admin", "password": "password", "path": "/var/run/zagg/data/remote_zagg", } ] }'

  #--net container:oso-rhel7-zaio \
docker run -ti --rm --name oso-rhel7-zagg-web \
  -e "ZAGG_SERVER_CONFIG=$ZAGG_SERVER_CONFIG" \
  -e "ZAGG_SERVER_USER=admin" \
  -e "ZAGG_SERVER_PASSWORD=password" \
  -e NAME=zagg-web -e IMAGE=zagg-web \
  -v /etc/localtime:/etc/localtime -v /var/lib/docker/volumes/shared/:/shared:rw \
  -p 8000:80 \
  oso-rhel7-zagg-web $1
