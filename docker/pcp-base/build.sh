#!/bin/bash -e

sudo echo -e "\nTesting sudo works...\n"

cd $(dirname $0)
sudo time docker build $@ -t pcp-base . && \
sudo docker tag -f pcp-base docker-registry.ops.rhcloud.com/ops/pcp-base
