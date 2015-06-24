#!/bin/bash -e

echo
echo 'Ensure database exists.'
echo '---------------'
/root/zabbix/createdb.sh
echo

echo
echo 'Starting crond'
echo '---------------'
/usr/sbin/crond -n
echo
