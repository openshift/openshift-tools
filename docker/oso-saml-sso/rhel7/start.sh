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

# this backgrounded block will run in 10 seconds
# after sshd and httpd have had a chance to start
# it's only point is to show in the logs that the
# processes are or aren't listening
{
  sleep 10
  echo
  echo 'list listening TCP sockets'
  echo '--------------------------'
  lsof -n -P -iTCP -sTCP:LISTEN
  echo
  echo 'startup complete'
} &

echo
echo 'start sshd'
echo '----------'
/usr/sbin/sshd
# give sshd a second to spit out any errors/warnings before launching httpd
sleep 1
echo
echo 'start httpd'
echo '-----------'
LANG=C /usr/sbin/httpd -DFOREGROUND
