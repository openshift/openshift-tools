#!/bin/bash -e

sudo echo -e "\nTesting sudo works...\n"

cd $(dirname $0)
sudo time docker build -t oso-rhel7-zabbix-server .
