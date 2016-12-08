#!/bin/bash

/usr/bin/mysqlshow -u${MYSQL_USER} -h${MYSQL_HOST} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} | grep -q trigger_discovery

if [ "$?" == 1 ]; then
  DBCREATEFILE=$(rpm -ql zabbix-server-mysql | grep 'create.sql')
  zcat $DBCREATEFILE | /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix
else
  echo "Database ${MYSQL_DATABASE} exists.  Skipping setup."
fi
