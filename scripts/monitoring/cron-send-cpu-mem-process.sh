#!/bin/bash
#check the mem and cpu use of the process
#the cpu use of node process
processidofnode=`ps -ef |grep '/usr/bin/openshift start node --config=/etc/origin/node/node-config.yaml'|grep -v "grep" |awk '{print $2}'`

CpuUsagenode=`ps -p $processidofnode -o %cpu |grep -v CPU`

echo "the cpu usage of openshift.node process is $CpuUsagenode"

MemUsagenode=`ps -p $processidofnode -o %mem |grep -v MEM`

echo "the mem usage of openshift.node process is $MemUsagenode"

ops-zagg-client -k "openshift.nodeprocess.cpu" -o "$CpuUsagenode"
ops-zagg-client -k "openshift.nodeprocess.mem" -o "$MemUsagenode"
