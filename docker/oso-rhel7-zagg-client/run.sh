#!/bin/bash

#docker run --rm=true -it --name zagg-client --privileged --ipc=host --net=host --pid=host -e HOST=/host -e NAME=zagg-client -e IMAGE=zagg-client -v /run:/run -v /var/log:/var/log -v /etc/localtime:/etc/localtime -v /:/host zagg-client $@
docker run --rm=true -it --name zagg-client \
           --privileged --ipc=host --net=host --pid=host \
           -e HOST=/host -e NAME=zagg-client -e IMAGE=zagg-client \
           -e CONTAINER_HOSTNAME=hostname -e ZAGG_SERVER=zagg-server -e ZAGG_PASSWORD=zagg-password \
           -v /var/log:/var/log -v /etc/localtime:/etc/localtime -v /:/host \
           -v /run/pcp:/run/pcp \
           zagg-client $@
