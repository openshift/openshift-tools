#!/bin/bash -e

echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd

# Configure the container on startup
ansible-playbook /root/config.yml

echo
echo 'Ensure database exists.'
echo '---------------'
/root/zabbix/createdb.sh
echo

echo
echo 'Starting zabbix agent'
echo '---------------'
/usr/sbin/zabbix_agentd -c /etc/zabbix/zabbix_agentd.conf
echo

echo
echo 'Starting zabbix'
echo '---------------'
/usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf
echo

while true; do
  sleep 5
done
#
