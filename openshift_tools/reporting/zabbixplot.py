#!/bin/env python

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
# Author: Jesse Kennedy <jessek@redhat.com>

"""Contains utilities for plotting data from Zabbix API"""

# Reason: Disable import checking for third party libraries
# Status: permanently disabled
# pylint: disable=import-error
from __future__ import print_function, division
import sys
import datetime
from operator import itemgetter
from itertools import groupby
from matplotlib import pyplot as plt
from matplotlib import dates as mdates, ticker
import numpy as np

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

# Reason: The use of data classes has not been decided
# Status: temporarily disabled until a decision is reached
# pylint: disable=too-few-public-methods
class ZabbixTimespan(object):
    """Data class for holding timespan-related objects"""
    def __init__(self, days):
        # TODO: Allow arbitrary end time
        self.time_start = datetime.datetime.now() - datetime.timedelta(days=days)
        self.time_end = datetime.datetime.now()
        self.timestamp_start = int(self.time_start.strftime("%s"))
        self.timestamp_end = int(self.time_end.strftime("%s"))
        self.mtime_start = mdates.date2num(self.time_start)
        self.mtime_end = mdates.date2num(self.time_end)

class ZabbixPlot(object):
    """Contains utilities for plotting data from Zabbix API"""

    # Reason: All of these parameters are needed
    # Status: permanently disabled
    # pylint: disable=too-many-arguments
    def __init__(self, zapi, group, trigger, timespan, limit):
        self.zapi = zapi
        self.group = group
        self.trigger = trigger
        self.timespan = timespan
        self.limit = limit

        self.events = None
        self.num_hosts = None

    def get_event_data(self):
        """Retrieve event data from Zabbix API"""
        # Warning: If there are variables in the description, they won't be filled in
        triggers = self.zapi.trigger.get(group=self.group, search={"description": self.trigger}, selectHosts="extend")
        triggerids = [t["triggerid"] for t in triggers]
        self.events = self.zapi.event.get(time_from=self.timespan.timestamp_start,
                                          time_till=self.timespan.timestamp_end, objectids=triggerids,
                                          limit=self.limit, selectHosts="extend", sortfield="clock", sortorder="DESC")
        if len(self.events) >= self.limit:
            print("Warning! Data has been truncated by the result limit. The graph will be inaccurate.",
                  file=sys.stderr)

    def get_num_hosts_in_group(self, group_name):
        """Retrieve the number of hosts in a hostgroup from Zabbix API"""
        self.num_hosts = int(self.zapi.hostgroup.get(filter={"name": group_name}, selectHosts="count")[0]["hosts"])

    @staticmethod
    def _calculate_event_downtime(event_value, event_clock, current_period_end, down):
        """Calculate the amount of downtime or uptime caused by an event"""
        # TODO: This will ignore events that start before the data
        if event_value != "0":
            # Add downtime, assuming this may be the last event
            return True, current_period_end - event_clock

        if event_value == "0" and down:
            # Remove downtime, compensating for recovered downtime
            return False, current_period_end - event_clock

        # Unchanged status of "up", and we're not recovering from downtime
        # Last event covered this time, so return a delta of zero
        return False, 0

    def _calculate_total_downtime(self, periods):
        """Calculates the total amount of downtime divided into periods (and number of nodes it found)"""
        period_func = lambda event: get_period(int(event["clock"]), periods)
        host_func = lambda event: event["hosts"][0]["hostid"]

        # Pre-fill time periods for graphing no downtime during a period
        downtime = {}
        for period in periods:
            downtime[period] = 0  # Yay

        for period_id, period_events in groupby(self.events, period_func):
            # Loop through periods
            current_period_end = get_next_period(period_id, periods)
            for _, host_events in groupby(period_events, host_func):
                # Loop through hosts in period
                is_down = False
                for event in host_events:
                    # Loop through events from this host
                    is_down, deltatime = self._calculate_event_downtime(event["value"], int(event["clock"]),
                                                                        current_period_end, is_down)
                    downtime[period_id] += deltatime
        return downtime

    def plot_aggregate(self, period_count):
        """Plots a bar chart from aggregated event occurences"""
        if self.events is None:
            self.get_event_data()
        if self.num_hosts is None:
            self.get_num_hosts_in_group(self.group)

        # Set up periods
        period_count += 1  # One more for the ending pseudo-period
        periods = np.linspace(self.timespan.timestamp_start, self.timespan.timestamp_end, num=period_count,
                              endpoint=True)
        period_seconds = (self.timespan.timestamp_end - self.timespan.timestamp_start) / (period_count - 1)

        downtime = self._calculate_total_downtime(periods)

        # Make downtime relative and a percentage
        downtime_list = sorted(downtime.items(), key=itemgetter(0))
        rel_downtime = np.array([i[1] / self.num_hosts / period_seconds * 100 for i in downtime_list])
        period2mdate = lambda p: mdates.date2num(datetime.datetime.fromtimestamp(p))
        times = np.array([period2mdate(i[0]) for i in downtime_list])

        # Create the plot
        _, axis = plt.subplots(figsize=(18, 10))
        width = period_seconds / 60.0 / 60.0 / 24.0  # 1 unit = 1 day
        plt.bar(times[:-1], rel_downtime[:-1], color="r", alpha=0.75, width=width)

        axis.set_xticks(times)
        axis.set_xlim(times[0], times[-1])
        axis.xaxis.set_major_formatter(mdates.DateFormatter('%a, %b %d %H:%M'))
        axis.xaxis.set_major_locator(ticker.FixedLocator(times))
        plt.setp(axis.get_xticklabels(), rotation=15, ha="right")
        plt.xlabel("Interval: " + str(datetime.timedelta(seconds=period_seconds)))

        plt.ylabel("Percent time in problem state")

        plt.title("Average percent time in \"" + self.trigger + "\" problem state over " +
                  str(self.num_hosts) + " nodes from " + self.timespan.time_start.strftime("%a, %b %d %H:%M") +
                  " to " + self.timespan.time_end.strftime("%a, %b %d %H:%M"))
        plt.tight_layout()

        plt.show()

    def plot_timeline(self):
        """Plots a timeline of events for hosts in a group"""
        if self.events is None:
            self.get_event_data()

        host_func = lambda event: event["hosts"][0]["name"]
        combo_func = lambda event: (event["hosts"][0]["name"], event["clock"])
        sorted_events = sorted(self.events, key=combo_func, reverse=False)

        _, axis = plt.subplots(figsize=(18, 10))
        height = 0.8  # Bar width

        hosts = []
        for _, host_events in groupby(sorted_events, host_func):
            # Loop through hosts
            plotted = False
            for event in host_events:
                # Loop through events from this host
                if not plotted:
                    # TODO: This will ignore events that start before the data
                    # Plot first left gray bar
                    hosts.append(event["hosts"][0]["host"].replace(".rhcloud.com", ""))
                    axis.barh(len(hosts) - 1, self.timespan.mtime_end - self.timespan.mtime_start,
                              left=self.timespan.mtime_start, height=0.8, alpha=1, color="0.95", linewidth=0, zorder=0)
                    plotted = True
                timestamp = mdates.date2num(datetime.datetime.fromtimestamp(int(event["clock"])))
                if event["value"] != "0":
                    # Event is in error state; plot event
                    axis.barh(len(hosts) - 1, self.timespan.mtime_end - timestamp, left=timestamp, height=0.8, alpha=1,
                              color="r", linewidth=0)
                else:
                    # Plot gray bar
                    axis.barh(len(hosts) - 1, self.timespan.mtime_end - timestamp, left=timestamp, height=0.8, alpha=1,
                              color="0.95", linewidth=0)

        # Set x axis bounds
        axis.set_xlim(self.timespan.mtime_start, self.timespan.mtime_end)
        # Rotate x axis labels
        plt.setp(axis.get_xticklabels(), rotation=15, ha="right")
        # Turn top horizontal tick marks off
        #plt.tick_params(axis='x', which="both", top="off")
        # Turn vertical gridlines on
        #axis.xaxis.grid(color="0", linestyle="--", linewidth=1)
        # Format x axis tick marks
        axis.xaxis.set_major_locator(mdates.AutoDateLocator())
        axis.xaxis.set_major_formatter(mdates.DateFormatter('%x %X'))
        axis.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))

        # Set y axis tick labels (height/2 for centering)
        plt.yticks(np.arange(len(hosts)) + height/2, hosts)
        # Set y axis label font size and turn off right vertical tick marks
        plt.tick_params(axis='y', labelsize=9, right="off")
        # Set y axis label
        plt.ylabel("Node")
        # Set y axis bounds
        axis.set_ylim(0, len(hosts))

        plt.title("\"" + self.trigger + "\" events from " +
                  self.timespan.time_start.strftime("%a, %b %d %H:%M") + " to " +
                  self.timespan.time_end.strftime("%a, %b %d %H:%M"))
        plt.tight_layout()

        plt.show()
