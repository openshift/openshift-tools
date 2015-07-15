#!/bin/bash -e

# Configure the container on startup
ansible-playbook /root/config.yml


# Start the services
echo 'Starting httpd'
echo '--------------'
LANG=C exec /usr/sbin/httpd -DFOREGROUND
