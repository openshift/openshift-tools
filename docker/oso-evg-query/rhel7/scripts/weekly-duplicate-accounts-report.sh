#!/bin/bash

/usr/local/bin/mysql_query -b -r -s $(date -d -7days +%Y-%m-%d) -e $(date -d +1days +%Y-%m-%d) -t
