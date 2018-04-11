#!/bin/bash -e

# This is useful so we can debug containers running inside of OpenShift that are
# failing to start properly.

if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo
  echo "This container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set."
  echo
  while true; do
    sleep 10    
  done
fi

echo "Running config playbook"
ansible-playbook /root/config.yml

echo This container hosts the following applications:
echo
echo '/bin/clam-scanner'
echo
echo '/usr/bin/image-inspector'
echo
echo '/usr/bin/scanpod-inmem'
echo
echo '/usr/local/bin/scanlog_listener'
echo
echo '/usr/local/bin/cron-scan-pods.sh'
echo
echo '/usr/local/bin/cron-in-memory-scan.sh'
echo
echo '/usr/local/bin/upload_scanlogs'
echo
echo '/usr/local/bin/orchestrator'

echo
echo 'Always listen for new containers. Container scanning queue will inspect one container at a time in FIFO order.'
echo '----------------'
/usr/local/bin/orchestrator &
echo 'Always listen for new scan logs. Scanning is scheduled once per day for all pods on the node.'
echo '----------------'
/usr/local/bin/scanlog_listener -s localhost -p 8080 -l /var/log/clam/scan.log &
echo 'Starting crond'
echo '---------------'
exec /usr/sbin/crond -n -m off
