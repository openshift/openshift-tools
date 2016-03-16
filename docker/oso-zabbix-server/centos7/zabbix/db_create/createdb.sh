#!/bin/bash

/usr/bin/mysqlshow -u${MYSQL_USER} -h${MYSQL_HOST} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} | grep -q trigger_discovery


if [ "$?" == 1 ]; then
  #/usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} < /root/zabbix/create_zabbix.sql
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/schema.sql
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/images.sql
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/data.sql
else
  echo "Database ${MYSQL_DATABASE} exists.  Skipping setup."
fi

