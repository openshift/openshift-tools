#!/bin/bash

cd $(dirname $0)
time docker build $@ -t oso-rhel7-zagg-web .
