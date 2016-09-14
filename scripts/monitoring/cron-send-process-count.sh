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
echo "Running: ops-zagg-client -k '$2' -o '$COUNT'"
ops-zagg-client -k "$2" -o "$COUNT"
ops-hawk-client -k "$2" -o "$COUNT"
echo
