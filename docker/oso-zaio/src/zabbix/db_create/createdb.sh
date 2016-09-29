#!/bin/bash -e

mysql -uroot < create_zabbix.sql

DBCREATEFILE=$(rpm -ql zabbix-server-mysql | grep 'create.sql')
zcat $DBCREATEFILE | /usr/bin/mysql -uroot zabbix
