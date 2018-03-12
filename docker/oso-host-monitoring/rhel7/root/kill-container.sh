#!/bin/bash
set -vx

echo "Killing container on request from autoheal script"

kill -9 $(cat /var/run/crond.pid)
