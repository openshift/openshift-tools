#!/usr/bin/env python
'''
   Command to send status of ovs to Zabbix
'''

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

import subprocess
from openshift_tools.monitoring.zagg_sender import ZaggSender

def get_vswitch_ports():
    ''' Get list of ports from ovs
    '''

    ## get list of running interfaces
    ovs_show_cmd = "/usr/bin/ovs-vsctl show"

    # get the output of ovs
    ovs_output = subprocess.check_output(ovs_show_cmd, shell=True)

    # pare down to only lines that contain "Port"
    running_port_list = [p for p in ovs_output.split('\n') if "Port" in p]

    return len(running_port_list)

def get_vswitch_pids():
    ''' Get list of ovs-related processes
    '''

    ## get list of ovs processes
    ovs_ps_cmd = "/usr/bin/pgrep -f 'ovsdb-server|ovs-vswitchd'"

    # get the output of ps
    ps_output = subprocess.check_output(ovs_ps_cmd, shell=True)

    return len(ps_output.split('\n'))

def main():
    ''' Get data and send to zabbix
    '''

    vswitch_ports_count = get_vswitch_ports()
    vswitch_pids_count = get_vswitch_pids()

    # we now have all the data we want.  Let's send it to Zagg
    zs = ZaggSender()
    zs.add_zabbix_keys({'vswitch_ports_count' : vswitch_ports_count})
    zs.add_zabbix_keys({'vswitch_pids_count' : vswitch_pids_count})

    # Finally, sent them to zabbix
    zs.send_metrics()

if __name__ == '__main__':
    main()
