#!/bin/bash

find /logs/$(date +%Y)/ -type d -ctime +10 -exec rm -rf {} +
