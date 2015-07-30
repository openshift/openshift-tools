#!/bin/bash

echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd

#getcap /usr/local/bin/start.sh
#ls -lZ /var/lib/
chown -R $(id -u).$(id -u) /var/lib/mysql/
#ls -lZ /var/lib/

echo 'prep db'
/usr/libexec/mariadb-prepare-db-dir
echo 'start db'
/usr/libexec/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib64/mysql/plugin --user=mysql --log-error=/var/log/mariadb/mariadb.log --pid-file=/var/run/mariadb/mariadb.pid &

echo "wait for db to come up"
sleep 5

echo 'populate zabbix db'
/root/createdb.sh

while true; do
  sleep 5
done
