#!/bin/bash

/usr/bin/mysqlshow -u${MYSQL_USER} -h ${MYSQL_HOST} ${MYSQL_DATABASE} &>/dev/null

if [ "$?" == 1 ]; then
  /usr/bin/mysql -uroot -h ${MYSQL_HOST} < /root/zabbix/create_zabbix.sql
  /usr/bin/mysql -uroot -h ${MYSQL_HOST} zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/schema.sql
  /usr/bin/mysql -uroot -h ${MYSQL_HOST} zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/images.sql
  /usr/bin/mysql -uroot -h ${MYSQL_HOST} zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/data.sql
else
  echo "Database ${MYSQL_DATABASE} exists.  Skipping setup."
fi

