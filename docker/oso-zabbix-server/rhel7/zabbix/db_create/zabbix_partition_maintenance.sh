#!/bin/sh

while true; do
  /usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "CALL partition_maintenance_all(\"${MYSQL_DATABASE}\");"

  sleep 21600
done
