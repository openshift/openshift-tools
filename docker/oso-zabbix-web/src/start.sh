#!/bin/bash -e

# This is useful so we can debug containers running inside of OpenShift that are
# failing to start properly.
if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo
  echo "This container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set."
  echo
  while sleep 10; do
    true
  done
fi


echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd

echo "Running config playbook"
ansible-playbook /root/config.yml

echo
echo 'start httpd'
echo '---------------'
LANG=C /usr/sbin/httpd -DFOREGROUND
