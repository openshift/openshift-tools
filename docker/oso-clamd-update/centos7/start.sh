#!/bin/bash -e

mypid=$$
registry=docker-registry.default.svc.cluster.local:5000
ns=$(cat /token/namespace)
imagename=clamsigs
tag=latest

declare -A already_have

if [ $mypid -eq 1 ]; then
  # allow somebody to "kill" us even though we're running as pid 1 in a Docker container
  trap "echo 'PID 1 received SIGTERM exiting!'; exit 1" SIGTERM
  trap "echo 'PID 1 received SIGINT exiting!'; exit 1" SIGINT
fi

# This is useful so we can debug containers running inside of OpenShift that are failing to start properly.
if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo -e "\nThis container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set.\n"
  while sleep 10; do true; done
fi

echo user:x:$(id -u):0:USER:/root:/bin/bash >> /etc/passwd
echo group:x:$(id -G | awk '{print $2}'):user >> /etc/group
mkdir -p /root/.kube

function check_token() {
  if [ "$token_version_dir" != "$(readlink -f /token/..data)" ]; then
    token_version_dir=$(readlink -f /token/..data)
    echo "$(date -Is) Adding cluster CAs to container CA bundle"
    update-ca-trust || :
    echo "$(date -Is) Generating new kube config from token"
    # note, the here doc must be indented with tabs since bash's <<-FOO doesn't support space-indented lines
    cat <<-EOF > /root/.kube/config
	apiVersion: v1
	clusters:
	- cluster:
	    server: https://openshift.default.svc.cluster.local
	  name: local_cluster
	contexts:
	- context:
	    cluster: local_cluster
	    namespace: $ns
	    user: sa_user
	  name: context
	current-context: context
	kind: Config
	preferences: {}
	users:
	- name: sa_user
	  user:
	    token: $(cat $token_version_dir/token)
	EOF
  fi
}

# loop forever, restarting the "oc get --watch" every time it disconnects for any reason
while true; do
  check_token
  # every change to our clamsigs:latest imagestreamtag will result in a loop iteration
  while read -r docker_image_ref; do
    check_token
    if [ -z "$docker_image_ref" ]; then
      continue # ignore -- for some reason we got an empty line
    fi
    echo "$(date -Is) Attempting to pull existing clamsigs bundle from $docker_image_ref"
    tmpdir=$(mktemp -d /var/lib/clamav/update_tmp_XXXXXXXXXXXXXXXXX)
    abort=0
    # we should really only ever have one layer per image, but just in case that assumption changes, we'll loop over the layers
    while read -r layer_blobsum; do
      if [ "${already_have["$layer_blobsum"]}" != 1 ]; then
        echo "$(date -Is) Attempting to pull clamsigs blob $layer_blobsum"
        boater get-blob -u unused --password-file /token/token $registry/$ns/$imagename@$layer_blobsum $layer_blobsum | tar -x -z -C "$tmpdir" -f - || \
          { abort=1; echo "$(date -Is) Apparent problem pulling image layer $registry/$ns/$imagename@$layer_blobsum.  Not updating"; break; }
        already_have["$layer_blobsum"]=1
      else
        echo "$(date -Is) Already have blob $layer_blobsum"
      fi
    done < <(boater get-manifest -u unused --password-file /token/token $docker_image_ref | grep -Po 'sha256:[a-f0-9]+')
    # only update if we didn't get an error above and if we have at least one new file in the update dir. *.* because db files all have an extension
    if [ "$abort" = 0 -a -n "$(find $tmpdir -maxdepth 1 -type f -name '*.*' -print -quit)" ]; then
      # remove any files that should no longer exist because they've been removed from the set of database files
      for file in $(find /var/lib/clamav -mindepth 1 -maxdepth 1 -type f); do
        if ! [ -f "$tmpdir/$(basename "$file")" ]; then
          rm -f "$file"
        fi
      done
      # move new files into place
      mv "$tmpdir"/* /var/lib/clamav
      # clean up
      rm -rf "$tmpdir"
      # notify clamd that we have new files
      clamdscan --reload || :
    fi
  done < <(oc get imagestream --watch $imagename \
               -o go-template='{{range .status.tags}}{{if eq .tag "latest"}}{{if lt 0 (len .items)}}{{index .items 0 "dockerImageReference"}}{{printf "\n"}}{{end}}{{end}}{{end}}')
  sleep 10  # wait a few seconds before reconnecting to the API service
done
