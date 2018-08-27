#!/bin/bash

# Disable Hyper-Threading at Runtime

# see https://access.redhat.com/solutions/352663
# preferred: /sys/devices/system/cpu/smt/control
# fallback: /sys/devices/system/cpu/cpu

if [ -f /sys/devices/system/cpu/smt/control ]; then
    echo off > /sys/devices/system/cpu/smt/control
else
    for CPU in $( ls /sys/devices/system/cpu/cpu[0-9]* -d | sort); 
    do 
        awk -F '[-,]' '{if(NF > 1) {HOTPLUG="/sys/devices/system/cpu/cpu"$NF"/online"; print "0" > HOTPLUG; close(HOTPLUG)}}' $CPU/topology/thread_siblings_list 2>/dev/null
    done
fi

# VERIFY
# Before will look something like this:
# /sys/devices/system/cpu/cpu0/topology/thread_siblings_list:0,2
# /sys/devices/system/cpu/cpu1/topology/thread_siblings_list:1,3
#
# After should look like this (no siblings):
# /sys/devices/system/cpu/cpu0/topology/thread_siblings_list:0
# /sys/devices/system/cpu/cpu1/topology/thread_siblings_list:1

THREAD_SIBLINGS=`grep '[^0-9]' /sys/devices/system/cpu/cpu*/topology/thread_siblings_list || true`
if [ "$THREAD_SIBLINGS" == "" ]; then
    exit 0
else  
    echo "Expected to find no thread siblings:"
    echo "$THREAD_SIBLINGS"
    exit 1
fi
