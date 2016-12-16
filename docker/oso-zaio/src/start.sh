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

echo
echo 'Running Ansible playbook'
echo '------------------------'
ansible-playbook /root/config.yml

echo
echo 'Preparing the db'
echo '----------------'
/usr/libexec/mariadb-prepare-db-dir
echo

echo -n 'Starting the db... '
/usr/libexec/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib64/mysql/plugin --user=mysql --log-error=/var/log/mariadb/mariadb.log --pid-file=/tmp/mariadb.pid  &
echo "Done."
echo

# FIXME: find a better way to manage this than with a simple sleep
echo -n 'Waiting 5 seconds for the db to come up... '
sleep 5
echo "Done."
echo

echo -n 'Populating the zabbix db... '
/root/createdb.sh
echo "Done."
echo

echo
echo 'Starting zabbix agent'
echo '---------------'
/usr/sbin/zabbix_agentd -c /etc/zabbix/zabbix_agentd.conf || :
echo

echo
echo 'Starting zabbix'
echo '---------------'
/usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf || :
echo

echo
echo 'Starting httpd'
echo '--------------'
/sbin/apachectl
echo

echo 'Restarting httpd'
echo '----------------'
killall httpd

# FIXME: find a better way to see when httpd is dead
echo -n 'Waiting 5 seconds for httpd to stop... '
sleep 5
echo "Done."
echo

echo
echo 'Starting httpd'
echo '--------------'
LANG=C /usr/sbin/httpd -DFOREGROUND
