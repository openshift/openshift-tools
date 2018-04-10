#!/bin/bash

/usr/local/bin/mysql_query -j $(date -d -7days +%Y-%m-%d) -k $(date -d +1days +%Y-%m-%d) -g 1 -a -t
