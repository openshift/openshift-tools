#!/usr/bin/env python
'''
  Command to send dynamic disk information to Zagg
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


import argparse
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.hawk_sender import HawkSender
from openshift_tools.monitoring import pminfo

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='Disk metric sender')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

    return parser.parse_args()

def clean_up_metric_dict(metric_dict, filter_string):
    """ Simple filter to elimate unnecessary characters in the key name """
    filtered_dict = {k.replace(filter_string, ''):v
                     for (k, v) in metric_dict.iteritems()
                     if not (v[0] == v[1] == 0)
                    }
    return filtered_dict

def main():
    """  Main function to run the check """

    args = parse_args()
    zagg_sender = ZaggSender(verbose=args.verbose, debug=args.debug)
    hawk_sender = HawkSender(verbose=args.verbose, debug=args.debug)

    discovery_key_disk = 'disc.disk'
    interval = 3
    pcp_disk_dev_metrics = ['disk.dev.total', 'disk.dev.avactive']
    item_prototype_macro_disk = '#OSO_DISK'
    item_prototype_key_tps = 'disc.disk.tps'
    item_prototype_key_putil = 'disc.disk.putil'

    disk_metrics = pminfo.get_sampled_data(pcp_disk_dev_metrics, interval, 2)

    pcp_metrics_divided = {}
    for metric in pcp_disk_dev_metrics:
        pcp_metrics_divided[metric] = {k: v for k, v in disk_metrics.items() if metric in k}

    # do TPS checks; use disk.dev.total
    filtered_disk_totals = clean_up_metric_dict(pcp_metrics_divided[pcp_disk_dev_metrics[0]],
                                                pcp_disk_dev_metrics[0] + '.')

    # Add dynamic items
    zagg_sender.add_zabbix_dynamic_item(discovery_key_disk, item_prototype_macro_disk, filtered_disk_totals.keys())
    #TODO: implement zagg_sender.add_zabbix_dynamic_item

    # calculate the TPS and add them to the ZaggSender
    for disk, totals in filtered_disk_totals.iteritems():
        disk_tps = (totals[1] - totals[0]) / interval
        zagg_sender.add_zabbix_keys({'%s[%s]' % (item_prototype_key_tps, disk): disk_tps})
        hawk_sender.add_zabbix_keys({'%s[%s]' % (item_prototype_key_tps, disk): disk_tps})

    # do % Util checks; use disk.dev.avactive
    filtered_disk_totals = clean_up_metric_dict(pcp_metrics_divided[pcp_disk_dev_metrics[1]],
                                                pcp_disk_dev_metrics[1] + '.')

    # calculate the % Util and add them to the ZaggSender
    for disk, totals in filtered_disk_totals.iteritems():
        total_active = (float)(totals[1] - totals[0]) / 1000.0
        putil = 100 * total_active / interval

        zagg_sender.add_zabbix_keys({'%s[%s]' % (item_prototype_key_putil, disk): putil})
        hawk_sender.add_zabbix_keys({'%s[%s]' % (item_prototype_key_putil, disk): putil})

    zagg_sender.send_metrics()
    hawk_sender.send_metrics()

if __name__ == '__main__':
    main()
