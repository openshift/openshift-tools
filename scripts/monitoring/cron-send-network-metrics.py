#!/usr/bin/env python
'''
  Command to send network information to Zagg
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

    parser = argparse.ArgumentParser(description='Network metric sender')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

    return parser.parse_args()

def clean_up_metric_dict(metric_dict, filter_string):
    """ Simple filter to elimate unnecessary characters in the key name """
    filtered_dict = {k.replace(filter_string, ''): v
                     for k, v in metric_dict.iteritems()
                     if not k.endswith('lo') and  v > 0
                    }

    return filtered_dict

def main():
    """  Main function to run the check """

    args = parse_args()
    zagg_sender = ZaggSender(verbose=args.verbose, debug=args.debug)
    hawk_sender = HawkSender(verbose=args.verbose, debug=args.debug)

    discovery_key_network = 'disc.network'
    pcp_network_dev_metrics = ['network.interface.in.bytes', 'network.interface.out.bytes']
    item_proto_macro_network = '#OSO_NET_INTERFACE'
    item_proto_key_in_bytes = 'disc.network.in.bytes'
    item_proto_key_out_bytes = 'disc.network.out.bytes'

    network_metrics = pminfo.get_metrics(pcp_network_dev_metrics)

    pcp_metrics_divided = {}
    for metric in pcp_network_dev_metrics:
        pcp_metrics_divided[metric] = {k: v for k, v in network_metrics.items() if metric in k}

    # do Network In; use network.interface.in.bytes
    filtered_network_totals = clean_up_metric_dict(pcp_metrics_divided[pcp_network_dev_metrics[0]],
                                                   pcp_network_dev_metrics[0] + '.')

    # Add dynamic items
    zagg_sender.add_zabbix_dynamic_item(discovery_key_network, item_proto_macro_network, filtered_network_totals.keys())
    #TODO: hawk_sender.add_zabbix_dynamic_item(discovery_key_network, item_proto_macro_network, filtered_network_totals.keys())

    # Report Network IN bytes; them to the ZaggSender
    for interface, total in filtered_network_totals.iteritems():
        zagg_sender.add_zabbix_keys({'%s[%s]' % (item_proto_key_in_bytes, interface): total})
        hawk_sender.add_zabbix_keys({'%s[%s]' % (item_proto_key_in_bytes, interface): total})

    # Report Network OUT Bytes;  use network.interface.out.bytes
    filtered_network_totals = clean_up_metric_dict(pcp_metrics_divided[pcp_network_dev_metrics[1]],
                                                   pcp_network_dev_metrics[1] + '.')

    # calculate the % Util and add them to the ZaggSender
    for interface, total in filtered_network_totals.iteritems():

        zagg_sender.add_zabbix_keys({'%s[%s]' % (item_proto_key_out_bytes, interface): total})
        hawk_sender.add_zabbix_keys({'%s[%s]' % (item_proto_key_out_bytes, interface): total})

    zagg_sender.send_metrics()
    hawk_sender.send_metrics()

if __name__ == '__main__':
    main()
