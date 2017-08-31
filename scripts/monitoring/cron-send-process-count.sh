#!/bin/bash

if [ $# -ne 2 ] ; then
  echo
  echo "Usage: $(basename $0) <process string> <metric key>"
  echo
  exit 1
fi

COUNT=$(pgrep -c -a -f "$1")
echo
echo "Number of processes matching [$1]: $COUNT"
echo
echo "Running: ops-metric-client -k '$2' -o '$COUNT'"
ops-metric-client -k "$2" -o "$COUNT"
echo
