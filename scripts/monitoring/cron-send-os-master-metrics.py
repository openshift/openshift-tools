#!/usr/bin/env python
'''
  Send Master information to Zagg
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
#from openshift_tools.monitoring.zagg_sender import ZaggSender
#from openshift_tools.monitoring import pminfo
import requests

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='Network metric sender')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

    return parser.parse_args()

def main():
    """  Main function to run the check """

    #HEALTHZ_URL = 'https://52.3.113.34/healthz'
    HEALTHZ_URL = 'https://52.23.178.108/healthz'
    #API_BASE_URL = 'https://52.3.113.34/api/v1'
    API_BASE_URL = 'https://52.23.178.108/api/v1'
    AUTH_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9wcy1tb25pdG9yLXRva2VuLXEwNWVvIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Im9wcy1tb25pdG9yIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNWE2MjAwNGMtODg5MC0xMWU1LWE4YmYtMGFlMzZjMTIzZTUxIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6b3BzLW1vbml0b3IifQ.cJuZMDJfqwonFdW9Nyfh0thGY0MugLnKWElEdi1oIA7n_Ut2CcHhFg_QofdwlB8hCdrWNVxEb-HZGnYIlSpDF04ocLWwaBU5Fz8NRZkcYUNRW2AKE1MQG0YVwzxQihq8Zgde_ZEIRa75faPTi8Lef1nE6TRKzWtktthTy7z2JapqOevkUFYc2sNQoLm_t-6xbGfYsPOkgdeY1gnD9_BDQXYhN7nx94rmK2OIj60voNlnOOSAxLcJ2538Af7bKYLdTSJ1mFJt-gN9iPy1l6qO81ChE6nDg6Fh0k8K2eNvMMKR-01mygG6cpQ0WoSWV4jmCGY2fAyhEjcYzJ6WLqVioA'
    AUTH_HEADER = {'Authorization': 'Bearer ' + AUTH_TOKEN}


    args = parse_args()

    resp = requests.get(HEALTHZ_URL, verify=False)
    print resp.text
    #print resp.json()

    resp = requests.get(API_BASE_URL + '/events', headers=AUTH_HEADER, verify=False)
    print resp.text
    print resp.json()
    response_json =  resp.json()
    print resp.json()['items']
    print len(resp.json()['items'])
    print response_json['items']
    print len(response_json['items'])



#    zagg_sender = ZaggSender(verbose=args.verbose, debug=args.debug)
#
#    discovery_key_network = 'disc.network'
#    pcp_network_dev_metrics = ['network.interface.in.bytes', 'network.interface.out.bytes']
#    item_proto_macro_network = '#OSO_NET_INTERFACE'
#    item_proto_key_in_bytes = 'disc.network.in.bytes'
#    item_proto_key_out_bytes = 'disc.network.out.bytes'
#
#    network_metrics = pminfo.get_metrics(pcp_network_dev_metrics)
#
#    pcp_metrics_divided = {}
#    for metric in pcp_network_dev_metrics:
#        pcp_metrics_divided[metric] = {k: v for k, v in network_metrics.items() if metric in k}
#
#    # do Network In; use network.interface.in.bytes
#    filtered_network_totals = clean_up_metric_dict(pcp_metrics_divided[pcp_network_dev_metrics[0]],
#                                                   pcp_network_dev_metrics[0] + '.')
#
#    # Add dynamic items
#    zagg_sender.add_zabbix_dynamic_item(discovery_key_network, item_proto_macro_network, filtered_network_totals.keys())
#
#    # Report Network IN bytes; them to the ZaggSender
#    for interface, total in filtered_network_totals.iteritems():
#        zagg_sender.add_zabbix_keys({'%s[%s]' % (item_proto_key_in_bytes, interface): total})
#
#    # Report Network OUT Bytes;  use network.interface.out.bytes
#    filtered_network_totals = clean_up_metric_dict(pcp_metrics_divided[pcp_network_dev_metrics[1]],
#                                                   pcp_network_dev_metrics[1] + '.')
#
#    # calculate the % Util and add them to the ZaggSender
#    for interface, total in filtered_network_totals.iteritems():
#
#        zagg_sender.add_zabbix_keys({'%s[%s]' % (item_proto_key_out_bytes, interface): total})
#
#    zagg_sender.send_metrics()

if __name__ == '__main__':
    main()
