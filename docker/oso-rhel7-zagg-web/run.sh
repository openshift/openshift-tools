#!/bin/bash

if [ $# -gt 0 ] ; then
  docker run -ti --rm --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /var/lib/docker/volumes/shared/:/shared:rw -p 8000:80 zagg-web $1
else
  docker run -d --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /var/lib/docker/volumes/shared/:/shared:rw -p 8000:80 zagg-web
fi
