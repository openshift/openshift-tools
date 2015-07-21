#!/bin/bash -e

echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd

echo
echo 'start httpd'
echo '---------------'
LANG=C /usr/sbin/httpd -DFOREGROUND
