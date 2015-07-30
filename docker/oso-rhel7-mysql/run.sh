#!/bin/bash

docker run -ti --name mysql -p 3306:3306 --rm=true -v /var/lib/docker/volumes/shared:/shared:rw oso-rhel7-mysql $@
