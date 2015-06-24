create database zabbix character set utf8 collate utf8_bin;
grant all privileges on zabbix.* to zabbix@localhost identified by 'redhat';
grant all privileges on zabbix.* to zabbix@'%' identified by 'redhat';
