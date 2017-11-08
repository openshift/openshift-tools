#!/bin/bash -e

SYSTEM_MAX_MEM=$(cat /sys/fs/cgroup/memory/system.slice/memory.max_usage_in_bytes)
SYSTEM_CURR_MEM=$(cat /sys/fs/cgroup/memory/system.slice/memory.usage_in_bytes)

KUBEPOD_MAX_MEM=$(cat /sys/fs/cgroup/memory/kubepods.slice/memory.max_usage_in_bytes)
KUBEPOD_CURR_MEM=$(cat /sys/fs/cgroup/memory/kubepods.slice/memory.usage_in_bytes)

echo "system.slice current: $SYSTEM_CURR_MEM"
echo "system.slice max:     $SYSTEM_MAX_MEM"

echo "kubepod.slice current: $KUBEPOD_CURR_MEM"
echo "kubepod.slice max:     $KUBEPOD_MAX_MEM"

ops-metric-client -k "mem.system.slice.current" -o "$SYSTEM_CURR_MEM"
ops-metric-client -k "mem.system.slice.max" -o "$SYSTEM_MAX_MEM"

ops-metric-client -k "mem.kubepod.slice.current" -o "$KUBEPOD_CURR_MEM"
ops-metric-client -k "mem.kubepod.slice.max" -o "$KUBEPOD_MAX_MEM"
