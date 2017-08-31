#!/bin/bash -e

# This is useful so we can debug containers running inside of OpenShift that are
# failing to start properly.
if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo
  echo "This container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set."
  echo
  while sleep 10; do
    true
  done
fi


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
  sleep 15
  pgrep -f "/usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf" &>/dev/null
  if [ "$?" -eq "1" ]
    then
      exit 1
  fi
done
#
