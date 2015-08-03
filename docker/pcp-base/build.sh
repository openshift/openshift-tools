#!/bin/bash -e


cd $(dirname $0)
time docker build $@ -t pcp-base . && \
docker tag -f pcp-base docker-registry.ops.rhcloud.com/ops/pcp-base
