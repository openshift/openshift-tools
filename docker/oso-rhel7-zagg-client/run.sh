#!/bin/bash

sudo docker run --rm=true -it --name oso-rhel7-zagg-client \
           --net=container:oso-f22-host-monitoring \
           -e ZAGG_SERVER=localhost                                             \
           -e ZAGG_USER=admin                                 \
           -e ZAGG_PASSWORD=zagg_server                         \
           -e ZAGG_CLIENT_HOSTNAME=localhost                                    \
           -e OSO_CLUSTER_GROUP=localhost                              \
           -e OSO_CLUSTER_ID=localhost                                   \
           -e OSO_HOST_TYPE=master      \
           -e OSO_SUB_HOST_TYPE=default                              \
           -v /etc/localtime:/etc/localtime                                              \
           -v /run/pcp:/run/pcp                                                          \
           -v /var/lib/docker/volumes/shared:/shared:rwZ \
           oso-rhel7-zagg-client $@
