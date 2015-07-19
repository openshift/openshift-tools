#!/bin/bash

cd $(dirname $0)
docker build $@ -t oso-rhel7-zagg-client .
