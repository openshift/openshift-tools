#!/bin/bash

/usr/bin/mysqlshow -u${MYSQL_USER} -h${MYSQL_HOST} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} | grep -q trigger_discovery

if [ "$?" == 1 ]; then
  mysql -uroot < "create database ${MYSQL_DATABASE} character set utf8 collate utf8_bin;"
  mysql -uroot < "grant all privileges on ${MYSQL_DATABASE}.* to ${MYSQL_USER}@localhost identified by '${MYSQL_PASSWORD}';"
  mysql -uroot < "grant all privileges on ${MYSQL_DATABASE}.* to ${MYSQL_USER}@'%' identified by '${MYSQL_PASSWORD}';"

else
  echo "Database ${MYSQL_DATABASE} exists. Skipping setup."
fi
