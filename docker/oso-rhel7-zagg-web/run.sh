#!/bin/bash


sudo echo -e "\nTesting sudo works...\n"

sudo docker run -ti --rm --name oso-rhel7-zagg-web \
  --link oso-rhel7-zaio:oso-rhel7-zaio \
  -e "ZAGG_SERVER_USER=admin" \
  -e "ZAGG_SERVER_PASSWORD=password" \
  -v /etc/localtime:/etc/localtime \
  -v /var/lib/docker/volumes/shared:/shared:rw \
  -p 8000:8000 \
  -p 8443:8443 \
  oso-rhel7-zagg-web $1
