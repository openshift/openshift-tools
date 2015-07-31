#!/bin/bash -e

cd $(dirname $0)
build docker build -t oso-rhel7-zabbix-web .
