#!/usr/bin/bash

host=$(hostname -s)
data=$(/usr/share/ansible/inventory/multi_inventory.py --refresh-cache 2>&1 1>/dev/null)

err_count=$(echo "$data" | wc -l)

if [ -n "$data"  ]; then
  # Log stderr from multi_inventory account refresh
  echo "$(date "+%F %T") $data" >> /var/log/multi_inventory.log
fi

# Send to zabbix
ops-zagg-client -s $host -k multi_inventory.account.refresh -o $err_count
