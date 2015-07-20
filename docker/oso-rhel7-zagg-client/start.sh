#!/bin/bash -e

# Configure the container
time ansible-playbook /root/config.yml

# Run the main service of this container
echo
echo 'Starting crond'
echo '---------------'
exec /usr/sbin/crond -n
echo
