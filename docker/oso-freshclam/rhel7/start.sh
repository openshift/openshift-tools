#!/bin/bash -e

mypid=$$

registry=docker-registry.default.svc.cluster.local:5000
ns=$(cat /pusher-token/namespace)
imagename=clamsigs
tag=latest


if [ $mypid -eq 1 ]; then
  # allow somebody to "kill" us even though we're running as pid 1 in a Docker container
  trap "echo 'PID 1 received SIGTERM exiting!'; exit 1" SIGTERM
  trap "echo 'PID 1 received SIGINT exiting!'; exit 1" SIGINT
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

token_version_dir=$(readlink -f /pusher-token/..data)
echo "$(date -Is) Adding cluster CAs to container CA bundle"
update-ca-trust || :

# Get any existing clamsigs
echo "$(date -Is) Attempting to pull existing clamsigs bundle from $registry/$ns/$imagename:$tag"
while read -r layer_blobsum; do
  boater get-blob -u unused --password-file /pusher-token/token $registry/$ns/$imagename@$layer_blobsum $layer_blobsum | tar -x -z -C /var/lib/clamav -f - || \
    echo "Apparent problem pulling image layer $registry/$ns/$imagename@$layer_blobsum.  Continuing"
done < <(boater get-manifest -u unused --password-file /pusher-token/token $registry/$ns/$imagename:$tag | grep -Po 'sha256:[a-f0-9]+')
find /var/lib/clamav -maxdepth 1 ! -name revts -type f | sort | xargs -r sha256sum > /tmp/sums_before_update.txt

# This block will run in a loop forever until this script is killed.
# Its job is to periodically run freshclam and push out new clamsig
# images when there are changes
while true; do
  if [ "$token_version_dir" != $(readlink -f /pusher-token/..data) ]; then
    token_version_dir=$(readlink -f /pusher-token/..data)
    echo "$(date -Is) Re-adding cluster CAs to container CA bundle"
    update-ca-trust || :
  fi
  echo "$(date -Is) Checking for signature updates"
  config_version_dir=$(readlink -f /clamsigs/..data)
  cp -a "$config_version_dir"/* /var/lib/clamav
  timeout -k 3900 3600 freshclam || :
  timeout -k 3900 3600 clamav-unofficial-sigs || :
  find /var/lib/clamav -maxdepth 1 ! -name revts -type f | sort | xargs -r sha256sum > /tmp/sums_after_update.txt
  if ! diff -q /tmp/sums_before_update.txt /tmp/sums_after_update.txt > /dev/null; then
    echo "$(date -Is) Updates found. Pushing new image."
    date -Is > /var/lib/clamav/revts
    # clean up any leftover temp cruft
    find /var/lib/clamav -mindepth 1 -maxdepth 1 -type d -print0 | xargs -r -0 rm -rf || :
    cd /var/lib/clamav && tar zcf /tmp/blob --no-recursion revts *.* && \
    blobsum=$(boater put-blob -u unused --password-file /pusher-token/token $registry/$ns/$imagename /tmp/blob)

    if [ $? -eq 0 -a -n "$blobsum" ]; then
      /root/make-manifest.yaml -e "namespace=$ns imagename=$ns blobsum=$blobsum" && \
      boater put-manifest -s -u unused --password-file /pusher-token/token $registry/$ns/$imagename:$tag /tmp/manifest.json
      if [ $? -eq 0 ]; then
        echo "$(date -Is) Successfully pushed new blob to $registry/$ns/$imagename:$tag"
        mv /tmp/sums_after_update.txt /tmp/sums_before_update.txt
      else
        echo $(date -Is) Apparent problem building or pushing image manifest.
      fi
    else
      echo $(date -Is) Apparent problem building or pushing image blob.
    fi
  else
    echo "$(date -Is) No updates found. Going back to sleep."
  fi
  # wait until the clamsigs secrets change or 2 hours    (rc of 2 means timeout occurred)
  inotifywait -t $((2*60*60)) -e DELETE_SELF "$config_version_dir" || [ $? -eq 2 ]
  sleep 5
  echo "$(date -Is): about to check for updates"
done
