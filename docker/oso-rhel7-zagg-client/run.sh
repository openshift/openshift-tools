#!/bin/bash

sudo docker run --rm=true -it --name oso-rhel7-zagg-client \
           --privileged \
           --pid=host \
           --net=container:oso-f22-host-monitoring \
           -e OSO_CLUSTER_GROUP=localcgrp                              \
           -e OSO_CLUSTER_ID=localcid                                   \
           -e OSO_HOST_TYPE=master      \
           -e OSO_SUB_HOST_TYPE=default                              \
           -v /etc/localtime:/etc/localtime                                              \
           -v /run/pcp:/run/pcp                                                          \
           -v /var/lib/docker/volumes/shared:/shared:rw \
           -v /var/run/docker.sock:/var/run/docker.sock \
           -v /var/run/openvswitch/db.sock:/var/run/openvswitch/db.sock \
           oso-rhel7-zagg-client $@
