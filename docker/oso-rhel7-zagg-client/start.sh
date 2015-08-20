#!/bin/bash -e

# Configure the container
time ansible-playbook /root/config.yml

# Send a heartbeat when the container starts up
/usr/bin/ops-zagg-client --send-heartbeat

# Run the main service of this container
echo
echo 'Starting crond'
echo '---------------'
exec /usr/sbin/crond -n
echo
