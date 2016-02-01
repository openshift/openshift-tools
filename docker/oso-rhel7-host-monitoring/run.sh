#!/bin/bash

# mwoodson note 1-7-16:
# pcp recommends mounting /run in their Dockerfile
#  /run conflicts with cron which also runs in this container.
# I am leaving /run out for now.  the guys in #pcp said that they mounted /run
#  to shared the pcp socket that is created in /run. We are not using this,
#  as far as I know.
#  This problem goes away with systemd being run in the containers and not using
#   cron but using systemd timers
#           -v /run:/run                                     \

sudo docker run --rm=true -it --name oso-rhel7-host-monitoring \
           --privileged                                     \
           --pid=host                                       \
           --net=host                                       \
           --ipc=host                                       \
           -e OSO_CLUSTER_GROUP=localcgrp                   \
           -e OSO_CLUSTER_ID=localcid                       \
           -e OSO_ENVIRONMENT=localprod                     \
           -e OSO_HOST_TYPE=master                          \
           -e OSO_SUB_HOST_TYPE=default                     \
           -e OSO_MASTER_HA=True                            \
           -v /etc/localtime:/etc/localtime:ro              \
           -v /sys:/sys:ro                                  \
           -v /sys/fs/selinux                               \
           -v /var/lib/docker:/var/lib/docker:ro            \
           -v /var/lib/docker/volumes/shared:/shared:rw     \
           -v /var/run/docker.sock:/var/run/docker.sock     \
           oso-rhel7-host-monitoring $@
