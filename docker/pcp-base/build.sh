#!/bin/bash -e


cd $(dirname $0)
time docker build $@ -t pcp-base .
