#!/bin/bash 
#
# For CVE-2016-8655
# Author: Joel Smith <joesmith@redhat.com>
# 15-Dec-2016
#
# anything older than this time will get restarted
cutoff_ts=$(date +%s -d '2016-12-15 01:05 UTC')

echo "Making a list of pods"

podlist=$(oc get pods --all-namespaces  -o jsonpath='{range .items[*]}{.metadata.namespace} {.metadata.name} {.metadata.creationTimestamp}{"\n"}{end}' | sort -R)

echo "Looking for old pods in the list"

# filter the podlist
filtered_podlist=""
while read -r ns name ts; do
  # leave "our" pods alone
  [ "$ns" = default -o "$ns" = management-infra -o "$ns" = openshift -o "$ns" = openshift-infra ] && continue
  ts=$(date +%s -d "$ts")
  # new pod, do not delete it
  [ "$ts" -gt "$cutoff_ts" ] && continue
  filtered_podlist="$filtered_podlist$ns $name $ts"$'\n'
done < <(echo "$podlist")

count="$(echo -n "$filtered_podlist" | wc -l)"

sleep_time=1
# For small clusters, sleep longer to try to minimize downtime for replicated pods
if [ "$count" -lt 100 ]; then
    sleep_time=10
fi
if [ "$count" -lt 30 ]; then
    sleep_time=30
fi

echo "Deleting $count pod(s), sleeping $sleep_time second(s) between deletes"

while read -r ns name ts; do
  echo oc delete pod -n "$ns" "$name"
  oc delete pod -n "$ns" "$name"
  # prevent a restart stampede by sleeping
  sleep $sleep_time
done < <(echo -n "$filtered_podlist")
