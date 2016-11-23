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
echo 'Running SSO functionality check every 24 hours'
echo '----------------'
/usr/local/bin/ops-run-in-loop 86400 "/usr/bin/flock -n /var/tmp/check_sso_service.lock -c '/usr/bin/timeout -s9 600s /usr/local/bin/check_sso_service.py &>> /var/log/monitor-sso.log'"
echo

echo
echo 'Running HTTP status check every 5 minutes'
echo '----------------'
/usr/local/bin/ops-run-in-loop 300 "/usr/bin/flock -n /var/tmp/check_sso_http_status.lock -c '/usr/bin/timeout -s9 600s /usr/local/bin/check_sso_http_status.py &>> /var/log/monitor-sso.log'"
