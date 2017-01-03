#!/bin/bash

# hacky script to send build counts. Replace with something nicer soon. 

oc get builds --all-namespaces -o yaml --config=/tmp/admin.kubeconfig \
  | grep phase | sort | uniq -c \
  | tr [:upper:] [:lower:] \
  | while read count name state; do
  ops-zagg-client -k "builds_running.${state}" -o "${count}"
done

ops-zagg-client -k "builds_running.total" -o "$(oc get builds --all-namespaces --no-headers --config=/tmp/admin.kubeconfig | wc -l)"
