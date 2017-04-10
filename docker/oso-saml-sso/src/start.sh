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
echo group:x:$(id -G | awk '{print $2}'):user >> /etc/group

# This backgrounded block will run in a loop forever.
# Its job is to monitor for secrets changes and
# re-run the config playbook when secrets change.
{
  set +e
  while true; do
    config_version_dir=$(readlink -f /secrets/..data)
    echo "Running config playbook"
    for attempt_number in {1..3}; do
      if ansible-playbook /root/config.yml; then
        break
      else
        echo "Pod configuration attempt #$attempt_number failed"
        if [ "$attempt_number" -eq 3 ]; then
          echo "Giving up, killing pod"
          kill -9 1
          exit
        else
          echo "Sleeping for $((10**attempt_number)) seconds before retry"
          sleep $((10**attempt_number))
        fi
      fi
    done
    if [ -f /var/run/sshd.pid ]; then
      echo "Reloading sshd config"
      pkill --signal HUP --pidfile /var/run/sshd.pid sshd
    fi
    touch /configdata/initial_config
    # wait until the secrets change
    inotifywait -e DELETE_SELF "$config_version_dir"
    sleep 5
  done
} &


echo "Waiting for initial configuration to finish"
while ! [ -f /configdata/initial_config ]; do
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
