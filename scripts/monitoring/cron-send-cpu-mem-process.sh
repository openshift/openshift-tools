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

#the cpu use of master api process


processidofmaster=`ps -ef |grep '/usr/bin/openshift start master api --config=/etc/origin/master/master-config.yaml'|grep -v "grep" |awk '{print $2}'`

if [ "$processidofmaster" != "" ];
then
    CpuUsagemasterapi=`ps -p $processidofmaster -o %cpu |grep -v CPU`

    echo "the cpu usage of openshift.master.api is $CpuUsagemasterapi"

    MemUsagemasterapi=`ps -p $processidofmaster -o %mem |grep -v MEM`

    echo "the mem usage of openshift.master.api is $MemUsagemasterapi"

    ops-zagg-client -k "openshift.master.api.cpu" -o "$CpuUsagenode"
    ops-zagg-client -k "openshift.master.api.mem" -o "$MemUsagenode"
else
    echo 
fi
