#!/bin/bash

XVDA2=$(/usr/bin/pminfo -f filesys.full | grep 'dev/xvda2' | awk '{print $NF}')
XVDA3=$(/usr/bin/pminfo -f filesys.full | grep 'dev/xvda3' | awk '{print $NF}')

/usr/bin/ops-zagg-client -k filesys.full.xvda2 -o $XVDA2
/usr/bin/ops-zagg-client -k filesys.full.xvda3 -o $XVDA3
