#!/bin/bash -e

mysql -uroot < create_zabbix.sql

mysql -uroot zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/schema.sql
mysql -uroot zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/images.sql
mysql -uroot zabbix < /usr/share/doc/zabbix-server-mysql-2.4.5/create/data.sql

