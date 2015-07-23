#!/bin/bash -e

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
/usr/local/bin/ops-run-in-loop 60 "/usr/bin/flock -n /var/tmp/ops-zagg-processor.lock -c '/usr/bin/timeout -s9 600s /usr/bin/ops-zagg-processor' &> /dev/null" &>> /var/log/ops-zagg-processor.log  &
echo "Done."


# Start the services
echo 'Starting httpd'
echo '--------------'
LANG=C exec /usr/sbin/httpd -DFOREGROUND
