#!/usr/bin/env python
'''
   Command to send count of running pods to Zabbix
'''

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

import subprocess
from openshift_tools.monitoring.zagg_sender import ZaggSender


def main():
    ''' Get data from oadm and send to zabbix
    '''

    ## set oadm config
    oadm_command = "KUBECONFIG=/etc/openshift/master/admin.kubeconfig /usr/bin/oadm"

    ## get list of running pods
    podlist_cmd = oadm_command + " manage-node --list-pods --selector=''"

    # get the output of oadm
    output = subprocess.check_output(podlist_cmd, shell=True)

    # pare down to only lines that contain "Running"
    running_pods_list = [p for p in output.split('\n') if "Running" in p]

    # we now have all the data we want.  Let's send it to Zagg
    zs = ZaggSender()
    zs.add_zabbix_keys({'running_pods_count' : len(running_pods_list)})

    # Finally, sent them to zabbix
    zs.send_metrics()

if __name__ == '__main__':
    main()
