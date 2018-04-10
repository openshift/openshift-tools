#!/bin/bash -e

echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd
echo group:x:$(id -G | awk '{print $2}'):user >> /etc/group

echo "Running config playbook"
ansible-playbook /root/config.yml

echo "Running weekly duplicate accounts report"
/usr/local/bin/weekly-duplicate-accounts-report.sh

exit 0
