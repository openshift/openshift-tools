#!/bin/bash

#
# Edit this, then copy and "compress" using ctrl-j
#
# This config works against a local ZAIO
#
#{
#  "targets": [
#    {
#      "name": "local cluster zbx server",
#      "type": "zabbix",
#      "trapper_server": "localhost",
#      "trapper_port": 10051,
#      "api_url": "http://localhost/zabbix/api_jsonrpc.php",
#      "api_user": "Admin",
#      "api_pass": "zabbix",
#      "path": "/var/run/zagg/data/cluster-zbx",
#    }
#  ]
#}
#


export ZAGG_SERVER_CONFIG='{ "targets": [ { "name": "local cluster zbx server", "type": "zabbix", "trapper_server": "localhost", "trapper_port": 10051, "api_url": "http://localhost/zabbix/api_jsonrpc.php", "api_user": "Admin", "api_pass": "zabbix", "path": "/var/run/zagg/data/cluster-zbx", } ] }'


docker run --net container:oso-rhel7-zaio -ti --rm --name oso-rhel7-zagg-web \
  -e "ZAGG_SERVER_CONFIG=$ZAGG_SERVER_CONFIG" \
  -e NAME=zagg-web -e IMAGE=zagg-web \
  -v /etc/localtime:/etc/localtime -v /var/lib/docker/volumes/shared/:/shared:rw \
  -p 8000:80 \
  oso-rhel7-zagg-web $1
