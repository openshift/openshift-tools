#!/bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

for line in $(chroot /host /usr/bin/docker ps -q); do echo "$line" && image-inspector -scan-type=clamav -clam-socket=/host/run/clamd.scan/clamd.sock -container="$line" -post-results-url http://localhost:8080; done
