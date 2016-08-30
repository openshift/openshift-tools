#!/bin/bash -e

# This is useful so we can debug containers running inside of OpenShift that are
# failing to start properly.
if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo
  echo "This container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set."
  echo
  while true ; do
    sleep 10
  done
fi


echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd

# Configure the container on startup
ansible-playbook /root/config.yml


# Temporary until we get cron working
# Send the heartbeat every 5 minutes
echo -n "Starting heartbeat loop... "
/usr/local/bin/ops-run-in-loop 300 /usr/bin/ops-zagg-heartbeater &>> /var/log/ops-zagg-heartbeater.log &
echo "Done."

echo -n "Sleeping 3 seconds to make sure the initial heartbeat has been added... "
sleep 3
echo "Done."


# Process and send metrics every minute
echo -n "Starting metric processing loop... "
/usr/local/bin/ops-run-in-loop 10 "/usr/bin/flock -n /var/tmp/ops-zagg-metric-processor.lock -c '/usr/bin/timeout -s9 600s /usr/bin/ops-zagg-metric-processor' &> /dev/null" &>> /var/log/ops-zagg-metric-processor.log  &
echo "Done."

# Process heartbeats every minute
echo -n "Starting heartbeat processing loop... "
/usr/local/bin/ops-run-in-loop 10 "/usr/bin/flock -n /var/tmp/ops-zagg-heartbeat-processor.lock -c '/usr/bin/timeout -s9 600s /usr/bin/ops-zagg-heartbeat-processor' &> /dev/null" &>> /var/log/ops-zagg-heartbeat-processor.log  &
echo "Done."


# Start the services
echo 'Starting httpd'
echo '--------------'
LANG=C exec /usr/sbin/httpd -DFOREGROUND
