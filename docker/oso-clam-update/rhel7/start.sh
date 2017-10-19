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

#echo "Running config playbook"
cd /var/lib/clamav/playbooks
ansible-playbook /var/lib/clamav/playbooks/config.yml

# Keep running freshclam and clamav-unofficial-sigs every 12 hours
echo
echo 'Updating ClamAV official signatures every 12 hours'
echo '----------------'
/usr/local/bin/ops-run-in-loop 43200 /usr/bin/freshclam &>/dev/null &
echo
# Pause for 5 minutes so they don't run at the same time
sleep 300
echo
echo 'Updating ClamAV unofficial signatures every 12 hours'
echo '----------------'
/usr/local/bin/ops-run-in-loop 43200 /usr/bin/clamav-unofficial-sigs.sh &>/dev/null &
# Pause for another 5 minutes and sync new files to the bucket
sleep 300
echo
echo 'Pushing signatures to bucket every 12 hours'
echo '----------------'
/usr/local/bin/ops-run-in-loop 43200 /usr/local/bin/push_clam_signatures &>/dev/null
# Pause for another 5 minutes and send timestamp info to zabbix
sleep 300
echo
echo 'Sending data to Zabbix every 12 hours'
echo '----------------'
/usr/local/bin/ops-run-in-loop 43200 /usr/local/bin/check_clam_update &>/dev/null
