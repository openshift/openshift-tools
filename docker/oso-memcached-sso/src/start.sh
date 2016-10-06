#!/bin/bash -e

# This is useful so we can debug containers running inside of OpenShift that are
# failing to start properly.
if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo
  echo "This container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set."
  echo
  while true ; do
    sleep 10
  done
fi


echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd
echo group:x:$(id -G | awk '{print $2}'):user >> /etc/group


echo "Running config playbook"
ansible-playbook /root/config.yml

echo
echo 'Starting memcached'
echo '----------------'
/usr/bin/memcached -m 64 -p 11211 -c 4096 -b 4096 -t 2 -R 200 -n 72 -f 1.25 -u memcached -o slab_reassign slab_automove
echo
