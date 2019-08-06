#!/bin/sh

zabbix_key_prefix=zabbix.db.partition.count.

while true; do
  tmp_file=$(/usr/bin/mktemp -p /tmp zabbix_tmp_patition_monitoring.XXXXX)
  current_epoch_date=$(/usr/bin/date +%s)

  for table in history history_log history_str history_text history_uint trends trends_uint; do

    # Run the query of how many future partitions exists
    partition_count=$(/usr/bin/mysql -sN -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT count(*) FROM information_schema.partitions  WHERE table_schema = 'zabbix' AND table_name = '${table}' AND partition_description >= ${current_epoch_date};")

    echo "\"Zabbix server\"  ${zabbix_key_prefix}${table}  ${partition_count}" >> ${tmp_file}

  done

  /usr/bin/zabbix_sender -i ${tmp_file} -z 127.0.0.1
  /usr/bin/rm -f /tmp/zabbix_tmp_patition_monitoring.*

  sleep 21600
done
