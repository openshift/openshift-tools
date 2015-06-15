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
# Purpose: Plots a timeline of events for hosts in a group

from __future__ import print_function, division
import argparse
from plot_common import ZabbixPlot

parser = argparse.ArgumentParser(description='Plots a timeline of events for hosts in a group')

parser.add_argument('-s', '--server', required=True, help='url of the Zabbix host (http://host/path/)')
parser.add_argument('-u', '--username', required=True, help='username')
parser.add_argument('-p', '--password', required=True, help='password')
parser.add_argument('-g', '--group', required=True, help='host group name')
parser.add_argument('-t', '--trigger', required=True,
                    help='trigger description (variables in the description will not be filled in)')
parser.add_argument('-d', '--days', default=7, type=float, help='days of data to retrieve (default: 7)')
parser.add_argument('-l', '--limit', default=25000, type=int, help='maximum number of events to fetch (default: 25000)')

args = parser.parse_args()

plot = ZabbixPlot(
    server=args.server,
    username=args.username,
    password=args.password,
    group=args.group,
    trigger=args.trigger,
    days=args.days,
    limit=args.limit
)

plot.plot_timeline()
