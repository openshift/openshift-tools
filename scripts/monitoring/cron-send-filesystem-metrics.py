#!/usr/bin/env python
'''
  Command to send dynamic filesystem information to Zagg
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2015 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring import pminfo

FILESYSTEM_METRIC = ['filesys.full']
DISCOVERY_KEY_FS = 'disc.filesys'
ITEM_PROTOTYPE_MACRO_FS = '#OSO_FILESYS'
ITEM_PROTOTYPE_KEY_FULL = 'disc.filesys.full'

FILESYS_METRICS = pminfo.get_metrics(FILESYSTEM_METRIC)

FILTERED_FILESYS_METRICS = {k.replace('filesys.full.', ''):v
                            for (k, v) in FILESYS_METRICS.iteritems()
                            if 'docker' not in k}

ZS = ZaggSender()
ZS.add_zabbix_dynamic_item(DISCOVERY_KEY_FS, ITEM_PROTOTYPE_MACRO_FS, FILTERED_FILESYS_METRICS.keys())

for filesys_name, filesys_full in FILTERED_FILESYS_METRICS.iteritems():
    ZS.add_zabbix_keys({'%s[%s]' % (ITEM_PROTOTYPE_KEY_FULL, filesys_name): filesys_full})

ZS.send_metrics()
