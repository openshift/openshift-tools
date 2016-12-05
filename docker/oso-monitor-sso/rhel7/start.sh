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

ts='{ print strftime("%Y-%m-%d %H:%M:%S"), $0; fflush(); }'

# Send a full heartbeat every 4 hours
/usr/local/bin/ops-run-in-loop $((60*60*4)) ops-runner -f -s 300 -n sso.monitoring.send.heartbeat.full /usr/bin/ops-zagg-client --send-heartbeat 2>&1 | awk "$ts" &
# Send a quick heartbeat every 5 minutes
/usr/local/bin/ops-run-in-loop $((60*5)) ops-runner -f -s 60 -n sso.monitoring.send.heartbeat.quick /usr/bin/ops-zagg-client  -k heartbeat.ping -o 1 2>&1 | awk "$ts" &

echo
echo 'Running SSO functionality check every 24 hours'
echo '----------------'
/usr/local/bin/ops-run-in-loop 86400 ops-runner -f -s 15 -n check.sso.iam.status /usr/local/bin/check_sso_service 2>&1 | awk "$ts" | tee /var/log/monitor-sso.log &
echo
echo 'Running container and HTTP status check every 5 minutes'
echo '----------------'
/usr/local/bin/ops-run-in-loop 300 ops-runner -f -s 15 -n check.sso.container.status /usr/local/bin/check_sso_http_status 2>&1 | awk "$ts" | tee /var/log/monitor-sso.log
