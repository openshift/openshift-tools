#!/bin/bash

docker run --rm=true -it --name zagg-client --privileged --ipc=host --net=host --pid=host -e HOST=/host -e NAME=zagg-client -e IMAGE=zagg-client -v /run:/run -v /var/log:/var/log -v /etc/localtime:/etc/localtime -v /:/host zagg-client
