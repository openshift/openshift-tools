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
# Wishlist: plot multiple triggers

# Reason: Disable import checking for third party libraries
# Status: permanently disabled
# pylint: disable=import-error
from __future__ import print_function, division
import sys
import datetime
import re
from collections import defaultdict
from operator import itemgetter
from itertools import groupby
from matplotlib import pyplot as plt, dates as mdates, ticker
import numpy as np

# Reason: DTO
# Status: permanently disabled
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
    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(self, zapi, group, trigger, timespan, limit, periods):
        self.zapi = zapi
        self.group = group
        self.trigger = trigger
        self.timespan = timespan
        self.limit = limit
        self.periods = periods + 1  # One more for the ending pseudo-period

        self.events = None
        self.num_hosts = None

    def plot(self):
        """Create both plots and show the user"""
        _, axes = plt.subplots(2, sharex=True, figsize=(16, 10))
        self.plot_timeline(axes[0])
        self.plot_aggregate(axes[1])
        axes[0].set_title("Time in \"" + self.trigger + "\" problem state over " + str(self.num_hosts) +
                          " hosts from " + self.timespan.time_start.strftime("%a, %b %d %H:%M") +
                          " to " + self.timespan.time_end.strftime("%a, %b %d %H:%M"), size=16)
        plt.tight_layout()
        plt.show()

    def get_event_data(self):
        """Retrieve event data from Zabbix API"""
        # Warning: If there are variables in the description, they won't be filled in
        triggers = self.zapi.trigger.get(group=self.group, search={"description": self.trigger}, limit=1)
        if len(triggers) == 0:
            raise Exception("No triggers found")
        # Replace trigger search term with full description and {variables} replaced with *
        self.trigger = re.sub(r"\{.*?\}", "*", triggers[0]["description"])
        print(self.trigger)
        # Find the rest of the triggers, searching by the first trigger found in order to prevent multiple triggers from
        # being mixed together
        triggers = self.zapi.trigger.get(group=self.group, search={"description": self.trigger},
                                         searchWildcardsEnabled=True)
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
    def get_period(timestamp, periods):
        """Gets the period a timestamp is in (the one to the left)"""
        for period in reversed(periods):
            if timestamp >= period:
                return period
        raise Exception("Timestamp not found in periods array")

    @staticmethod
    def get_next_period(timestamp, periods):
        """Gets the period after a timestamp (the one to the right)"""
        for period in periods:
            if timestamp < period:
                return period
        raise Exception("Next timestamp not found in periods array")

    @staticmethod
    def _calculate_anomaly_downtime(event_clock, periods, downtime):
        # UNUSED: Innaccurate
        """Assume we missed the beginning downtime event and retroactively apply downtime to periods"""
        current_period = periods[0]
        downtime[current_period] = 0
        while event_clock > current_period:
            next_period = ZabbixPlot.get_next_period(current_period, periods)
            if event_clock <= next_period:
                # Downtime ends in this period
                downtime[current_period] += event_clock - current_period
            else:
                # Downtime ends in another period
                downtime[current_period] += next_period - current_period
            current_period = next_period
        return

    @staticmethod
    def _calculate_event_downtime(event_value, event_clock, host_id, down_since):
        """Calculate the amount of downtime or uptime caused by an event"""
        if event_value != "0":
            # Going down
            if host_id not in down_since:
                # Host was up
                down_since[host_id] = event_clock
                return 0
            else:
                # Host was already down
                return 0
        else:  # event_value == "0":
            # Coming up
            if host_id in down_since:
                # Host was down
                # print("host", host_id, "was down since", down_since[host_id])
                return event_clock - down_since.pop(host_id)
            else:
                # Host was already up (did we miss the beginning downtime event?)
                return 0

    def _calculate_total_downtime(self, periods):
        """Calculates the total amount of downtime divided into periods (and number of nodes it found)"""
        period_func = lambda event: ZabbixPlot.get_period(int(event["clock"]), periods)
        host_func = lambda event: event["hosts"][0]["name"]
        combo_func = lambda event: (event["clock"], event["hosts"][0]["name"])
        sorted_events = sorted(self.events, key=combo_func, reverse=False)

        # Pre-fill time periods for graphing no downtime during a period
        downtime = {}
        for period in periods:
            downtime[period] = 0  # Yay
        down_since = {}

        for period_id, period_events in groupby(sorted_events, period_func):
            # Loop through periods
            current_period_end = ZabbixPlot.get_next_period(period_id, periods)
            for host_id, host_events in groupby(period_events, host_func):
                # Loop through hosts in period
                for event in host_events:
                    # Loop through events from this host
                    deltatime = self._calculate_event_downtime(event["value"], int(event["clock"]), host_id, down_since)
                    if deltatime is None:
                        self._calculate_anomaly_downtime(int(event["clock"]), periods, downtime)
                    else:
                        # print("adding", deltatime, "to", datetime.datetime.fromtimestamp(period_id))
                        downtime[period_id] += deltatime
            for host in down_since:
                # Go through unclosed downtime, add rest of period to downtime, set since to end of this period
                downtime[period_id] += current_period_end - down_since[host]
                down_since[host] = current_period_end
        return downtime

    def plot_aggregate(self, axis):
        """Plots a bar chart from aggregated event occurences"""
        if self.events is None:
            self.get_event_data()
        if self.num_hosts is None:
            self.get_num_hosts_in_group(self.group)

        # Set up periods
        periods = np.linspace(self.timespan.timestamp_start, self.timespan.timestamp_end, num=self.periods,
                              endpoint=True)
        period_seconds = (self.timespan.timestamp_end - self.timespan.timestamp_start) / (self.periods - 1)

        downtime = self._calculate_total_downtime(periods)

        # Make downtime relative and a percentage
        downtime_list = sorted(downtime.items(), key=itemgetter(0))
        rel_downtime = np.array([i[1] / self.num_hosts / period_seconds * 100 for i in downtime_list])
        period2mdate = lambda p: mdates.date2num(datetime.datetime.fromtimestamp(p))
        times = np.array([period2mdate(i[0]) for i in downtime_list])

        # Create the plot
        plt.sca(axis)
        width = period_seconds / 60.0 / 60.0 / 24.0  # 1 unit = 1 day
        plt.bar(times[:-1], rel_downtime[:-1], color="r", alpha=0.75, width=width)

        axis.set_xticks(times)
        axis.set_xlim(times[0], times[-1])
        axis.xaxis.set_major_formatter(mdates.DateFormatter('%a, %b %d %H:%M'))
        axis.xaxis.set_major_locator(ticker.FixedLocator(times))
        plt.setp(axis.get_xticklabels(), rotation=15, ha="right")
        axis.set_xlabel("Interval: " + str(datetime.timedelta(seconds=period_seconds)))

        axis.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: str(x) + "%"))
        axis.set_ylabel("Site-wide unavailability")

        # plt.show()

    def plot_timeline(self, axis):
        """Plots a timeline of events for hosts in a group"""
        if self.events is None:
            self.get_event_data()

        host_func = lambda event: event["hosts"][0]["name"]
        combo_func = lambda event: (event["hosts"][0]["name"], event["clock"])
        sorted_events = sorted(self.events, key=combo_func, reverse=False)

        plt.sca(axis)
        height = 0.8  # Bar width

        host_bars = defaultdict(list)
        host_downtime = defaultdict(float)
        hosts_seen = set()
        for host_id, host_events in groupby(sorted_events, host_func):
            # Loop through hosts
            for event in host_events:
                timestamp = mdates.date2num(datetime.datetime.fromtimestamp(int(event["clock"])))
                if event["value"] != "0":
                    # Event is in error state; plot event
                    hosts_seen.add(host_id)
                    host_downtime[host_id] += self.timespan.mtime_end - timestamp
                    host_bars[host_id].append((self.timespan.mtime_end - timestamp, timestamp, "r", 1))
                elif host_id in hosts_seen:
                    host_downtime[host_id] -= self.timespan.mtime_end - timestamp
                    host_bars[host_id].append((self.timespan.mtime_end - timestamp, timestamp, "0.95", 1))
        i = 0
        ordered_hosts = sorted(host_downtime.items(), key=lambda (k, v): v)
        for host_tuple in ordered_hosts:
            if host_tuple[1] > 0:
                axis.barh(i, self.timespan.mtime_end - self.timespan.mtime_start, left=self.timespan.mtime_start,
                          height=height, color="0.95", linewidth=0, zorder=0)
                for point in host_bars[host_tuple[0]]:
                    axis.barh(i, point[0], left=point[1], height=height, color=point[2], zorder=point[3], linewidth=0)
                i += 1

        # # Set x axis bounds
        # axis.set_xlim(self.timespan.mtime_start, self.timespan.mtime_end)
        # # Rotate x axis labels
        # plt.setp(axis.get_xticklabels(), rotation=15, ha="right")
        # # Turn top horizontal tick marks off
        # #plt.tick_params(axis='x', which="both", top="off")
        # # Turn vertical gridlines on
        # #axis.xaxis.grid(color="0", linestyle="--", linewidth=1)
        # # Format x axis tick marks
        # axis.xaxis.set_major_locator(mdates.AutoDateLocator())
        # axis.xaxis.set_major_formatter(mdates.DateFormatter('%x %X'))
        # axis.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))

        # Create a list of hostnames from list of tuples
        keys = [host[0] for host in ordered_hosts if host[1] > 0]
        # Set y axis tick labels (height/2 for centering)
        axis.set_yticks(np.arange(len(keys)) + height/2)
        axis.set_yticklabels(keys)
        # Set y axis label font size and turn off right vertical tick marks
        plt.tick_params(axis='y', labelsize=9, right="off")
        # Set y axis label
        axis.set_ylabel("Node")
        # Set y axis bounds
        axis.set_ylim(0, len(keys))

        # plt.show()
