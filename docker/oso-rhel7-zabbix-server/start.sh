#!/bin/bash -e

echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd

sed -ri -e "s/^DBUser=.*/DBUser=${MYSQL_USER}/g" \
        -e "s/^DBPassword=.*/DBPassword=${MYSQL_PASSWORD}/g" \
        -e "s/^DBHOst=.*/DBHost=${MYSQL_HOST}/g" /etc/zabbix/zabbix_server.conf


echo
echo 'Ensure database exists.'
echo '---------------'
/root/zabbix/createdb.sh
echo

# Clean up the extra templates
echo
echo 'Clean up zabbix templates'
echo '---------------'
ansible-playbook /root/ansible/playbooks/clean_zabbix.yml
echo

# Create the heartbeat and os linux templates along with items
echo
echo 'Create zabbix templates'
echo '---------------'
ansible-playbook /root/ansible/playbooks/setup_zabbix.yml
echo

echo
echo 'Starting zabbix agent'
echo '---------------'
/usr/sbin/zabbix_agentd -c /etc/zabbix/zabbix_agentd.conf
echo

echo
echo 'Starting zabbix'
echo '---------------'
/usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf
echo

while true; do
  sleep 5
done

