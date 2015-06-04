#!/bin/bash -e

echo 'start httpd'
LANG=C /usr/sbin/httpd -DFOREGROUND
