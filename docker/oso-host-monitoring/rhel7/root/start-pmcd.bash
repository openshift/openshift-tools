#!/bin/bash -e

# original source: https://github.com/redhat-developer/osd-monitor-poc/blob/master/pcp-node-collector/run-pmcd.sh

: "${PCP_HOSTNAME:=`hostname`}"

# Adjust to OSD/OSO? AWS conventions: ip-172-31-51-101.ec2.internal => NODE-ip-172-31-51-101
PCP_NODE_HOSTNAME=NODE-`echo $PCP_HOSTNAME | cut -f1 -d.`

# Setup pmcd to run in unprivileged mode of operation
. /etc/pcp.conf

# allow unauthenticated access to proc.* metrics (default is false)
export PROC_ACCESS=1
export PMCD_ROOT_AGENT=0


# NB: we can't use the rc.pmcd script.  It assumes that it's run as root.
cd $PCP_VAR_DIR/pmns
./Rebuild

cd $PCP_LOG_DIR
exec /usr/libexec/pcp/bin/pmcd -A -f -l /dev/no-such-file -H $PCP_NODE_HOSTNAME
