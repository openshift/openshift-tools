#!/bin/bash

#docker run --rm=true -it --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /home/mwoodson/docker-dev:/docker-dev zagg-web
#docker run --rm -ti --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /home/mwoodson/docker-dev:/docker-dev zagg-web
docker run -d --name zagg-web --privileged -e NAME=zagg-web -e IMAGE=zagg-web  -v /etc/localtime:/etc/localtime -v /home/mwoodson/docker-dev:/docker-dev -p 8000:80 zagg-web
