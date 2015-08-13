#!/bin/bash -e

sudo docker run -ti --rm --privileged --net=host --pid=host --ipc=host -v /sys:/sys:ro  -v /etc/localtime:/etc/localtime:ro -v /var/lib/docker:/var/lib/docker:ro -v /run:/run -v /var/log:/var/log -v /var/lib/docker/volumes/shared:/shared:rw --name=oso-f22-host-monitoring oso-f22-host-monitoring $@
