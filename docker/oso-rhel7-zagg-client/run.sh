#!/bin/bash

docker run --rm=true -it --name oso-rhel7-zagg-client \
           --privileged --ipc=host --net=host --pid=host \
           -e HOST=/host -e NAME=oso-rhel7-zagg-client -e IMAGE=oso-rhel7-zagg-client \
           -v /var/log:/var/log -v /etc/localtime:/etc/localtime -v /:/host \
           -v /var/lib/docker/volumes/shared/:/shared:rwZ \
           -v /var/lib/docker/volumes/secrets/:/secrets:rwZ \
           -v /run/pcp:/run/pcp \
           oso-rhel7-zagg-client $@
