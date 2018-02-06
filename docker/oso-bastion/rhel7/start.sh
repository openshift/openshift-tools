#!/bin/bash

# Make sure the script exits on error
set +e

persistent_dir=/persistent

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


# Setup the user in passwd and group
echo user:x:$(id -u):0:USER:${persistent_dir}:/bin/bash >> /etc/passwd
echo group:x:0:user >> /etc/group


# Make a directory for sshd persistentce
mkdir -p ${persistent_dir}/.ssh
chmod 700 ${persistent_dir}/.ssh


# TODO: Add step where ${persistent_dir}/.ssh/authorized_keys is populated from /configdata


# Setup default bashrc if one doesn't exist
if [ ! -f "${persistent_dir}/.bashrc" ]; then
    cp /root/.bashrc "${persistent_dir}/.bashrc"
fi

# Setup default bash_profile if one doesn't exist
if [ ! -f "${persistent_dir}/.bash_profile" ]; then
    cp /root/.bashrc "${persistent_dir}/.bash_profile"
fi



# Generate ssh host keys if they don't exist in the persistent storage
ssh_host_key_path=${persistent_dir}/.ssh/ssh_host_rsa_key
if [ ! -f "${ssh_host_key_path}" ]; then
    ssh-keygen -f "${ssh_host_key_path}" -N '' -t rsa
fi


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
