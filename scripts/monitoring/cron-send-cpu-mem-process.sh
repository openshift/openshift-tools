#!/bin/bash
#check the mem and cpu use of the process
#the cpu use of node process
processidofnode=`ps -ef |grep '/usr/bin/openshift start node --config=/etc/origin/node/node-config.yaml'|grep -v "grep" |awk '{print $2}'`

CpuUsagenode=`ps -p $processidofnode -o %cpu |grep -v CPU`

echo "the cpu usage of openshift.node process is $CpuUsagenode%"

MemUsagenode=`ps -p $processidofnode -o %mem |grep -v MEM`

echo "the mem usage of openshift.node process is $MemUsagenode%"

ops-zagg-client -k "openshift.nodeprocess.cpu" -o "$CpuUsagenode"
ops-zagg-client -k "openshift.nodeprocess.mem" -o "$MemUsagenode"

#the cpu use of master api process


processidofmaster=`ps -ef |grep '/usr/bin/openshift start master api --config=/etc/origin/master/master-config.yaml'|grep -v "grep" |awk '{print $2}'`

if [ "$processidofmaster" != "" ];
then
    CpuUsagemasterapi=`ps -p $processidofmaster -o %cpu |grep -v CPU`

    echo "the cpu usage of openshift.master.api is $CpuUsagemasterapi%"

    MemUsagemasterapi=`ps -p $processidofmaster -o %mem |grep -v MEM`

    echo "the mem usage of openshift.master.api is $MemUsagemasterapi%"

    ops-zagg-client -k "openshift.master.api.cpu" -o "$CpuUsagenode"
    ops-zagg-client -k "openshift.master.api.mem" -o "$MemUsagenode"
else
    echo 
fi


#the cpu use of etcd 

processidofetcd=`ps -ef |grep '/usr/bin/etcd'|grep -v "grep" |awk '{print $2}'`

if [ "$processidofetcd" != "" ];
then
    CpuUsageetcd=`ps -p $processidofetcd -o %cpu |grep -v CPU`

    echo "the cpu usage of openshift.etcd is $CpuUsageetcd%"

    MemUsageetcd=`ps -p $processidofetcd -o %mem |grep -v MEM`

    echo "the mem usage of openshift.etcd is $MemUsageetcd%"

    ops-zagg-client -k "openshift.etcd.cpu" -o "$CpuUsageetcd"
    ops-zagg-client -k "openshift.etcd.mem" -o "$MemUsageetcd"
else
    echo 
fi


#docker daemon

processidofdocker=`ps -ef |grep '/usr/bin/docker daemon --selinux-enabled'|grep -v "grep" |awk '{print $2}'`

CpuUsagedocker=`ps -p $processidofdocker -o %cpu |grep -v CPU`

echo "the cpu usage of docker daemon is $CpuUsagedocker%"

MemUsagedocker=`ps -p $processidofdocker -o %mem |grep -v MEM`

echo "the mem usage of docker daemon is $MemUsagedocker%"

ops-zagg-client -k "openshift.docker.daemon.cpu" -o "$CpuUsageetcd"
ops-zagg-client -k "openshift.docker.daemon.mem" -o "$MemUsageetcd"


