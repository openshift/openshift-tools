#!/bin/bash

while getopts c:t: option
do
case "${option}"
in
c) CLUSTERNAME=${OPTARG};;
t) NODETYPE=${OPTARG};;
esac
done

INTERNAL_HOSTNAME=$(curl 169.254.169.254/latest/meta-data/local-hostname)

nohup /usr/bin/redhat-access-insights --register --display-name=$CLUSTERNAME-$NODETYPE-$INTERNAL_HOSTNAME --group=$CLUSTERNAME &
