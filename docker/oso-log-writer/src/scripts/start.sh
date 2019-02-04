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

echo This container hosts the following applications:
echo
echo '/usr/local/bin/log-writer'
echo
echo '/usr/local/bin/clean.sh'


echo
echo 'Every 12 hours, clean up pod log dirs that are older than 30 days.'
echo '----------------'
/usr/local/bin/ops-run-in-loop 43200 /usr/local/bin/clean.sh & 
echo
echo 'Always listen for pod logs from pod-logger pods.'
echo '----------------'
/usr/local/bin/log-writer
