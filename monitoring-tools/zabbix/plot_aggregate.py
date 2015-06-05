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
parser.add_argument('-n', '--num-hosts', type=int, 
    help='number of hosts contained in host group. the default is the number ' \
    'of hosts seen in the returned data, but this number will exclude hosts with no events.')
parser.add_argument('-c', '--periods', type=int, 
    help='number of periods to display (default: number of days)')
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



period_count = (args.periods or args.days) + 1  # One more for the ending pseudo-period
periods = np.linspace(timestamp_start, timestamp_end, num=period_count, endpoint=True)
period_seconds = (timestamp_end - timestamp_start) / (period_count - 1)

def get_period(timestamp):
    for p in reversed(periods):
        if timestamp >= p:
            return p
    raise Exception("Timestamp not found in periods array")

def get_next_period(timestamp):
    for p in periods:
        if timestamp < p:
            return p
    raise Exception("Next timestamp not found in periods array")

host_func = lambda event : event["hosts"][0]["hostid"]
time_func = lambda event : event["clock"]
combo_func = lambda event : (event["clock"], event["hosts"][0]["hostid"])
period_func = lambda event : get_period(int(event["clock"]))
period2mdate = lambda p : mdates.date2num(datetime.datetime.fromtimestamp(p))

sorted_events = sorted(events, key=combo_func, reverse=False)

# Pre-fill time periods for graphing no downtime during a period
downtime = {}
for p in periods:
    downtime[p] = 0  # Yay

nodes = set()
rows = 0
for period_id, period_events in groupby(sorted_events, period_func):
    current_period_end = get_next_period(period_id)
    for host_id, host_events in groupby(period_events, host_func):
        nodes.add(host_id)
        down = False
        for event in host_events:
            rows += 1
            # TODO: This will ignore events that start before the data
            if event["value"] != "0":
                # Add downtime, assuming this may be the last event
                downtime[period_id] += current_period_end - int(event["clock"])
                down = True
            elif event["value"] == "0" and down:
                # Compensate for recovered downtime
                downtime[period_id] -= current_period_end - int(event["clock"])
                down = False
if rows >= args.limit:
    print("Warning! Data has been truncated by the result limit. The graph " \
    "will be inaccurate.", file=sys.stderr)
node_count = args.num_hosts or len(nodes)

# Make downtime relative and a percentage
downtime_list = sorted(downtime.items(), key=itemgetter(0))
rel_downtime = np.array([i[1] / node_count / period_seconds * 100 for i in downtime_list])
times = np.array([period2mdate(i[0]) for i in downtime_list])

fig, ax = plt.subplots(figsize=(18, 10))
ax = plt.gca()
width = period_seconds / 60.0 / 60.0 / 24.0  # 1 unit = 1 day
plt.bar(times[:-1], rel_downtime[:-1], color="r", alpha=0.75, width=width)

ax.set_xticks(times)
ax.set_xlim(times[0], times[-1])
ax.xaxis.set_major_formatter(mdates.DateFormatter('%a, %b %d %H:%M'))
ax.xaxis.set_major_locator(ticker.FixedLocator(times))
#ax.xaxis.set_major_locator(mdates.AutoDateLocator())
plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
plt.xlabel("Interval: " + str(datetime.timedelta(seconds=period_seconds)))

# Set y axis label
plt.ylabel("% time in problem state")

plt.title("Average percent time in \"" + args.trigger + "\" problem state over " + 
    str(node_count) + " nodes from " + time_start.strftime("%a, %b %d %H:%M") + 
    " to " + time_end.strftime("%a, %b %d %H:%M"))
plt.tight_layout()

plt.show()
