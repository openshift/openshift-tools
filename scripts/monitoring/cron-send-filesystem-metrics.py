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

ZS = ZaggSender(verbose=True)
FILESYS_FULL_METRIC = ['filesys.full']
FILESYS_INODE_DERIVED_METRICS = {'filesys.inodes.pused' :
                                 'filesys.usedfiles / (filesys.usedfiles + filesys.freefiles) * 100'
                                }

DISCOVERY_KEY_FS = 'disc.filesys'
ITEM_PROTOTYPE_MACRO_FS = '#OSO_FILESYS'

ITEM_PROTOTYPE_KEY_FULL = 'disc.filesys.full'
ITEM_PROTOTYPE_KEY_INODE = 'disc.filesys.inodes.pused'

def filter_out_docker_filesystems(metric_dict, filesystem_filter):
    """ Simple filter to elimate unnecessary characters in the key name """
    filtered_dict = {k.replace(filesystem_filter, ''):v
                     for (k, v) in metric_dict.iteritems()
                     if 'docker' not in k
                    }
    return filtered_dict


# Get the disk space
FILESYS_FULL_METRICS = pminfo.get_metrics(FILESYS_FULL_METRIC)

FILTERED_FILESYS_METRICS = filter_out_docker_filesystems(FILESYS_FULL_METRICS, 'filesys.full.')

ZS.add_zabbix_dynamic_item(DISCOVERY_KEY_FS, ITEM_PROTOTYPE_MACRO_FS, FILTERED_FILESYS_METRICS.keys())
for filesys_name, filesys_full in FILTERED_FILESYS_METRICS.iteritems():
    ZS.add_zabbix_keys({'%s[%s]' % (ITEM_PROTOTYPE_KEY_FULL, filesys_name): filesys_full})


# Get filesytem inode metrics
FILESYS_INODE_METRICS = pminfo.get_metrics(derived_metrics=FILESYS_INODE_DERIVED_METRICS)

FILTERED_FILESYS_INODE_METRICS = filter_out_docker_filesystems(FILESYS_INODE_METRICS, 'filesys.inodes.pused.')
for filesys_name, filesys_inodes in FILTERED_FILESYS_INODE_METRICS.iteritems():
    ZS.add_zabbix_keys({'%s[%s]' % (ITEM_PROTOTYPE_KEY_INODE, filesys_name): filesys_inodes})


ZS.send_metrics()
