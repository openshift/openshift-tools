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
# Purpose: Contains utilities for plotting data from Zabbix API

from __future__ import print_function, division
import sys
import datetime
from operator import itemgetter
from itertools import groupby
from matplotlib import pyplot as plt
from matplotlib import dates as mdates, ticker
import numpy as np
from pyzabbix import ZabbixAPI

def get_period(timestamp, periods):
    """Gets the period a timestamp is in (the one to the left)"""
    for period in reversed(periods):
        if timestamp >= period:
            return period
    raise Exception("Timestamp not found in periods array")

def get_next_period(timestamp, periods):
    """Gets the period after a timestamp (the one to the right)"""
    for period in periods:
        if timestamp < period:
            return period
    raise Exception("Next timestamp not found in periods array")

class ZabbixPlot(object):
    """Contains utilities for plotting data from Zabbix API"""

    def get_event_data(self):
        """Retrieve event data from Zabbix API"""
        # Using a double negative because empty arrays are truthy
        if self.events is not False:
            return self.events
        # Warning: If there are variables in the description, they won't be filled in
        triggers = self.zapi.trigger.get(group=self.group, search={"description": self.trigger}, selectHosts="extend")
        triggerids = [t["triggerid"] for t in triggers]
        self.events = self.zapi.event.get(time_from=self.timestamp_start, time_till=self.timestamp_end,
                                         triggerids=triggerids, limit=self.limit, selectHosts="extend",
                                         sortfield="clock", sortorder="DESC")

    def __init__(self, server, username, password, group, trigger, days, limit):
        self.server = server
        self.username = username
        self.password = password
        self.group = group
        self.trigger = trigger
        self.days = days
        self.limit = limit

        self.time_start = datetime.datetime.now() - datetime.timedelta(days=days)
        self.time_end = datetime.datetime.now() - datetime.timedelta(days=0)
        self.timestamp_start = int(self.time_start.strftime("%s"))
        self.timestamp_end = int(self.time_end.strftime("%s"))
        self.mtime_start = mdates.date2num(self.time_start)
        self.mtime_end = mdates.date2num(self.time_end)

        self.zapi = ZabbixAPI(self.server)
        self.zapi.login(self.username, self.password)
        self.events = False

    def plot_aggregate(self, periods, num_hosts):
        """Plots a bar chart from aggregated event occurences"""
        self.get_event_data()

        period_count = (periods or self.days) + 1  # One more for the ending pseudo-period
        periods = np.linspace(self.timestamp_start, self.timestamp_end, num=period_count, endpoint=True)
        period_seconds = (self.timestamp_end - self.timestamp_start) / (period_count - 1)

        host_func = lambda event: event["hosts"][0]["hostid"]
        period_func = lambda event: get_period(int(event["clock"]), periods)
        period2mdate = lambda p: mdates.date2num(datetime.datetime.fromtimestamp(p))

        # Pre-fill time periods for graphing no downtime during a period
        downtime = {}
        for period in periods:
            downtime[period] = 0  # Yay

        nodes = set()
        rows = 0
        for period_id, period_events in groupby(self.events, period_func):
            current_period_end = get_next_period(period_id, periods)
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
        if rows >= self.limit:
            print("Warning! Data has been truncated by the result limit. The graph " \
            "will be inaccurate.", file=sys.stderr)
        node_count = num_hosts or len(nodes)

        # Make downtime relative and a percentage
        downtime_list = sorted(downtime.items(), key=itemgetter(0))
        rel_downtime = np.array([i[1] / node_count / period_seconds * 100 for i in downtime_list])
        times = np.array([period2mdate(i[0]) for i in downtime_list])

        # Create the plot
        fig, axis = plt.subplots(figsize=(18, 10))
        width = period_seconds / 60.0 / 60.0 / 24.0  # 1 unit = 1 day
        plt.bar(times[:-1], rel_downtime[:-1], color="r", alpha=0.75, width=width)

        axis.set_xticks(times)
        axis.set_xlim(times[0], times[-1])
        axis.xaxis.set_major_formatter(mdates.DateFormatter('%a, %b %d %H:%M'))
        axis.xaxis.set_major_locator(ticker.FixedLocator(times))
        #axis.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(axis.get_xticklabels(), rotation=15, ha="right")
        plt.xlabel("Interval: " + str(datetime.timedelta(seconds=period_seconds)))

        # Set y axis label
        plt.ylabel("% time in problem state")

        plt.title("Average percent time in \"" + self.trigger + "\" problem state over " +
                  str(node_count) + " nodes from " + self.time_start.strftime("%a, %b %d %H:%M") +
                  " to " + self.time_end.strftime("%a, %b %d %H:%M"))
        plt.tight_layout()

        plt.show()

    def plot_timeline(self):
        """Plots a timeline of events for hosts in a group"""
        self.get_event_data()

        host_func = lambda event: event["hosts"][0]["name"]
        time_func = lambda event: event["clock"]
        combo_func = lambda event: (event["hosts"][0]["name"], event["clock"])
        sorted_events = sorted(self.events, key=combo_func, reverse=False)

        fig, axis = plt.subplots(figsize=(18, 10))
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
                    axis.barh(len(hosts), self.mtime_end - self.mtime_start, left=self.mtime_start, height=0.8, alpha=1,
                              color="0.95", linewidth=0)
                    plotted = True
                timestamp = mdates.date2num(datetime.datetime.fromtimestamp(int(event["clock"])))
                if event["value"] != "0":
                    # Event is in error state; plot event
                    axis.barh(len(hosts), self.mtime_end - timestamp, left=timestamp, height=0.8, alpha=1,
                              color="r", linewidth=0)
                elif event["value"] == "0":
                    # Plot gray bar
                    axis.barh(len(hosts), self.mtime_end - timestamp, left=timestamp, height=0.8, alpha=1,
                              color="0.95", linewidth=0)
            if plotted:
                hosts.append(event["hosts"][0]["host"].replace(".rhcloud.com", ""))
        if rows >= self.limit:
            print("Warning! Data has been truncated by the result limit. The graph " \
                "will be inaccurate.", file=sys.stderr)

        # Set x axis bounds
        axis.set_xlim(self.mtime_start, self.mtime_end)
        # Rotate x axis labels
        plt.setp(axis.get_xticklabels(), rotation=15, ha="right")
        # Turn top horizontal tick marks off
        #plt.tick_params(axis='x', which="both", top="off")
        # Turn vertical gridlines on
        #axis.xaxis.grid(color="0", linestyle="--", linewidth=1)
        # Format x axis labels
        axis.xaxis.set_major_locator(mdates.AutoDateLocator())
        axis.xaxis.set_major_formatter(mdates.DateFormatter('%x %X'))
        axis.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
        # Set x axis title
        #plt.xlabel("Time")

        # Set y axis tick labels (height/2 for centering)
        plt.yticks(np.arange(len(hosts)) + height/2, hosts)
        # Set y axis label font size and turn off right vertical tick marks
        plt.tick_params(axis='y', labelsize=9, right="off")
        # Set y axis label
        plt.ylabel("Node")
        # Set y axis bounds
        axis.set_ylim(0, len(hosts))

        plt.title("\"" + self.trigger + "\" events from " +
                  self.time_start.strftime("%a, %b %d %H:%M") + " to " +
                  self.time_end.strftime("%a, %b %d %H:%M"))
        plt.tight_layout()

        plt.show()
