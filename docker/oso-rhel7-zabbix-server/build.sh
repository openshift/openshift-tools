#!/bin/bash -e

cd $(dirname $0)
docker build -t oso-rhel7-zabbix-server .
