#!/bin/bash

sudo docker run --rm=true -it --name oso-rhel7-zagg-client \
           --net=container:oso-f22-host-monitoring \
           -v /var/lib/docker/volumes/shared:/shared:rwZ \
           -v /run/pcp:/run/pcp \
           oso-rhel7-zagg-client $@
