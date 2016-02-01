#!/usr/bin/env python
'''
   Command to send nodes that are not in ready state
'''

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

import subprocess
from openshift_tools.monitoring.zagg_sender import ZaggSender

def get_node_status():
    ''' Get node status from masters
    '''

    ## get list of running interfaces
    get_nodes_cmd = "/usr/bin/oc get nodes"

    # get the output of ovs
    nodes_output = subprocess.check_output(get_nodes_cmd, shell=True)

    # pare down to only lines that contain "hostname"
    node_status_list = [n for n in nodes_output.split('\n') if "hostname" in n]

    return node_status_list

def main():
    ''' Get data and send to zabbix
    '''

    nodes_output = get_node_status()

    nodes_not_schedulable = [n for n in nodes_output if "SchedulingDisabled " in n]

    nodes_not_ready = [n for n in nodes_output if "NotReady" in n]

    print "Found %s nodes not schedulable"  % len(nodes_not_schedulable)
    print "Found %s nodes not ready" % len(nodes_not_ready)

    # we now have all the data we want.  Let's send it to Zagg
    zs = ZaggSender()
    zs.add_zabbix_keys({'openshift.node.not.schedulable.count' : vswitch_ports_count})
    zs.add_zabbix_keys({'openshift.node.not.ready.count' : vswitch_pids_count})

    # Finally, sent them to zabbix
    zs.send_metrics()

if __name__ == '__main__':
    main()
