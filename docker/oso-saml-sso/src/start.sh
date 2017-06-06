#!/bin/bash -e

mypid=$$

if [ $mypid -eq 1 ]; then
  # allow somebody to "kill" us even though we're running as pid 1 in a Docker container
  trap "echo 'PID 1 received SIGTERM (from liveness or readiness probe?), exiting!'; exit 1" SIGTERM
  trap "echo 'PID 1 received SIGINT (failed reconfigure?), exiting!'; exit 1" SIGINT
fi

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
echo group:x:$(id -G | awk '{print $2}'):user >> /etc/group
reconf_touchfile="/configdata/reconfigure_successful"

# This backgrounded block will run in a loop forever.
# Its job is to monitor for secrets changes and
# re-run the config playbook when secrets change.
{
  set +e
  while true; do
    config_version_dir=$(readlink -f /secrets/..data)
    echo "Running config playbook"
    for attempt_number in {1..3}; do
      rm -f "$reconf_touchfile"
      if ansible-playbook /root/config.yml -e config_success_touchfile="$reconf_touchfile"; then
        # if the playbook is successful, it will touch $reconf_touchfile as its final task
        if [ -f "$reconf_touchfile" ]; then
          break
        else
          failmsg="ansible-playbook /root/config.yml apparent failure. Final task to touch $reconf_touchfile was not run"
        fi
      else
        failmsg="ansible-playbook /root/config.yml failed with exit status $?"
      fi
      echo "Pod configuration attempt #$attempt_number failed: $failmsg"
      if [ "$attempt_number" -eq 3 ]; then
        echo "Giving up, killing pod"
        kill -INT $mypid
        sleep 1
        kill -KILL $mypid
        exit
      else
        echo "Sleeping for $((10**attempt_number)) seconds before retry"
        sleep $((10**attempt_number))
      fi
    done
    if [ -f /var/run/sshd.pid ]; then
      echo "Reloading sshd config"
      pkill --signal HUP --pidfile /var/run/sshd.pid sshd
    fi
    if [ -f /var/run/httpd/httpd.pid ]; then
      echo "Reloading httpd config"
      pkill --signal USR1 --pidfile /var/run/httpd/httpd.pid httpd
    fi
    # wait until the secrets change
    inotifywait -e DELETE_SELF "$config_version_dir"
    sleep 5
  done
} &


echo "Waiting for initial configuration to finish"
while ! [ -f "$reconf_touchfile" ]; do
  sleep 1
done

# this backgrounded block will run in 10 seconds
# after sshd and httpd have had a chance to start
# its only point is to show in the logs that the
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
