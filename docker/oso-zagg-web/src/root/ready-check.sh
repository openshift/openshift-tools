#!/bin/bash -e
set -vx

max_llen=$1
if [[ -z $1 ]]; then
    echo "Please run script with maximum set"
    echo "$0 num"
    echo "$0 20000"
    exit 2
fi

llen=`redis-cli llen "local cluster zbx server"`

if [[ llen -gt max_llen ]]; then
    exit 1
fi

exit 0
