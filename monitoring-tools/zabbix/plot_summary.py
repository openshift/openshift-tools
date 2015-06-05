#!/bin/env python2
 
# Copyright 2015 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#  Author: Jesse Kennedy <jessek@redhat.com>
# Purpose: Plots an aggregate summary of Zabbix trigger events, divided by
#          time periods

from __future__ import print_function, division
import time
import sys
import datetime
import argparse
from operator import itemgetter
from itertools import groupby
from matplotlib import pyplot as plt
from matplotlib import dates as mdates, ticker
import numpy as np
from pyzabbix import ZabbixAPI

parser = argparse.ArgumentParser(description='Plots an aggregate summary of ' \
    'Zabbix trigger events, divided by time periods')

parser.add_argument('-s', '--server', required=True,
    help='url of the Zabbix host (http://host/path/)')
parser.add_argument('-u', '--username', required=True,
    help='username')
parser.add_argument('-p', '--password', required=True,
    help='password')
parser.add_argument('-g', '--group', required=True,
    help='host group name')
parser.add_argument('-t', '--trigger', required=True,
    help='trigger description (variables in the description will not be filled in)')
parser.add_argument('-d', '--days', default=7, type=int,
    help='days of data to retrieve (default: 7)')
parser.add_argument('-l', '--limit', default=25000, type=int,
    help='maximum number of events to fetch (default: 25,000)')

args = parser.parse_args()

zapi = ZabbixAPI(args.server)
zapi.login(args.username, args.password)



time_start = datetime.datetime.now() - datetime.timedelta(days=args.days)
time_end = datetime.datetime.now() - datetime.timedelta(days=0)

timestamp_start = int(time_start.strftime("%s"))
timestamp_end = int(time_end.strftime("%s"))
mtime_start = mdates.date2num(time_start)
mtime_end = mdates.date2num(time_end)

# Warning: If there are variables in the description, they won't be filled in
triggers = zapi.trigger.get(group=args.group, search={"description": args.trigger}, 
    selectHosts="extend")
triggerids = [t["triggerid"] for t in triggers]
events = zapi.event.get(time_from=timestamp_start, time_till=timestamp_end, 
    objectids=triggerids, limit=args.limit, selectHosts="extend", 
    sortfield="clock", sortorder="DESC")



host_func = lambda event : event["hosts"][0]["hostid"]
time_func = lambda event : event["clock"]
combo_func = lambda event : (event["hosts"][0]["hostid"], event["clock"])
sorted_events = sorted(events, key=combo_func, reverse=False)

fig, ax = plt.subplots(figsize=(18, 10))
height = 0.8  # Bar width

rows = 0
hosts = []
for host_id, host_events in groupby(sorted_events, host_func):
    plotted = False
    for event in host_events:
        rows += 1
        if not plotted:
            # TODO: This will ignore events that start before the data
            # Plot first left gray bar
            ax.barh(len(hosts), mtime_end - mtime_start, left=mtime_start, 
                height=0.8, alpha=1, color="0.95", linewidth=0)
            plotted = True
        timestamp = mdates.date2num(datetime.datetime.fromtimestamp(int(event["clock"])))
        if event["value"] != "0":
            # Event is in error state; plot event
            ax.barh(len(hosts), mtime_end - timestamp, left=timestamp, 
                height=0.8, alpha=1, color="r", linewidth=0)
        elif event["value"] == "0":
            # Plot gray bar
            ax.barh(len(hosts), mtime_end - timestamp, left=timestamp, 
                height=0.8, alpha=1, color="0.95", linewidth=0)
    if plotted:
        hosts.append(event["hosts"][0]["host"].replace(".rhcloud.com",""))
if rows >= args.limit:
    print("Warning! Data has been truncated by the result limit. The graph " \
        "will be inaccurate.", file=sys.stderr)

# Set x axis bounds
ax.set_xlim(mtime_start, mtime_end)
# Rotate x axis labels
plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
# Turn top horizontal tick marks off
#plt.tick_params(axis='x', which="both", top="off")
# Turn vertical gridlines on
#ax.xaxis.grid(color="0", linestyle="--", linewidth=1)
# Format x axis labels
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%x %X'))
ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0,6,12,18]))
# Set x axis title
#plt.xlabel("Time")

# Set y axis tick labels (height/2 for centering)
plt.yticks(np.arange(len(hosts)) + height/2, hosts)
# Set y axis label font size and turn off right vertical tick marks
plt.tick_params(axis='y', labelsize=9, right="off")
# Set y axis label
plt.ylabel("Node")
# Set y axis bounds
ax.set_ylim(0, len(hosts))

plt.title("\"" + args.trigger + "\" events from " + 
    time_start.strftime("%a, %b %d %H:%M") + " to " + 
    time_end.strftime("%a, %b %d %H:%M"))
plt.tight_layout()

plt.show()
