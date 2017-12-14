#!/bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

for line in $(chroot /host /usr/bin/docker ps --format 'table {{.ID}} {{.Image}} {{.Command}} {{.CreatedAt}} {{.Status}} {{.Ports}} {{.Label "io.kubernetes.pod.namespace"}} {{.Names}}' | awk '{if (NR>1 && $NF !~ /^k8s_POD/ && $(NF-1) !~ /^openshift-/ && $(NF-1) !~ "logging" && $NF !~ /^oso-rhel7-host-monitoring/) print $1;}'); do image-inspector -scan-type=clamav -clam-socket=/host/run/clamd.scan/clamd.sock -container="$line" -post-results-url http://localhost:8080; done

/usr/local/bin/upload_scanlogs
