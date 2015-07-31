#!/bin/bash -e


cd $(dirname $0)
time docker build $@ -t oso-f22-host-monitoring .
