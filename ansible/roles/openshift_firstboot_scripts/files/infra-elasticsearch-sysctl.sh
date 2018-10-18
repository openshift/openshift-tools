#!/bin/bash

/usr/bin/echo "vm.max_map_count=262144" > "/etc/sysctl.d/99-elasticsearch.conf"
/usr/sbin/sysctl --system
