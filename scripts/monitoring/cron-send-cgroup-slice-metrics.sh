#!/bin/bash -e

SYSTEM_CURR_MEM=$(cat /sys/fs/cgroup/memory/system.slice/memory.stat | awk '/^total_rss / { print $2 }')

KUBEPOD_CURR_MEM=$(cat /sys/fs/cgroup/memory/kubepods.slice/memory.stat | awk '/^total_rss / { print $2 }')

DOCKER_CURR_MEM=$(cat /sys/fs/cgroup/memory/system.slice/docker.service/memory.stat | awk '/^total_rss / { print $2 }')

ATOMIC_OPENSHIFT_NODE_CURR_MEM=$(cat /sys/fs/cgroup/memory/system.slice/atomic-openshift-node.service/memory.stat | awk '/^total_rss / { print $2 }')

echo "system.slice current: $SYSTEM_CURR_MEM"

echo "kubepod.slice current: $KUBEPOD_CURR_MEM"

echo "docker.service current: $DOCKER_CURR_MEM"

echo "aos-node current: $ATOMIC_OPENSHIFT_NODE_CURR_MEM"

ops-metric-client -k "mem.system.slice.current" -o "$SYSTEM_CURR_MEM"

ops-metric-client -k "mem.kubepod.slice.current" -o "$KUBEPOD_CURR_MEM"

ops-metric-client -k "mem.docker.service.current" -o "$DOCKER_CURR_MEM"

ops-metric-client -k "mem.aos-node.service.current" -o "$ATOMIC_OPENSHIFT_NODE_CURR_MEM"
