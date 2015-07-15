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


if [ $# -gt 0 ] ; then
  docker run -e "ZAGG_SERVER_CONFIG=$ZAGG_SERVER_CONFIG" -ti --rm --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /var/lib/docker/volumes/shared/:/shared:rw -p 8000:80 zagg-web $1
else
  docker run -e "ZAGG_SERVER_CONFIG=$ZAGG_SERVER_CONFIG" -d --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /var/lib/docker/volumes/shared/:/shared:rw -p 8000:80 zagg-web
fi
