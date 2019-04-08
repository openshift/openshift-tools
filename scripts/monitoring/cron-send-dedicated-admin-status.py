#!/usr/bin/env python
'''
   Command to send status of ovs to Zabbix
'''

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

import subprocess
from openshift_tools.monitoring.zagg_sender import ZaggSender

def get_dedicated_admin_pids():
    ''' get the pid of service dedicated-admin
    '''

    dedicated_admin_ps_cmd = "/usr/bin/pgrep -f apply-dedicated-roles"

    # get the output of ps
    ps_output = subprocess.check_output(dedicated_admin_ps_cmd, shell=True)

    return len(ps_output.strip().split('\n'))

def main():
    ''' Get data and send to zabbix
    '''

    dedicated_admin_count = get_dedicated_admin_pids()

    # we now have all the data we want.  Let's send it to Zagg
    zs = ZaggSender()
    zs.add_zabbix_keys({'openshift.master.service.dedicated.admin.count' : dedicated_admin_count})

    # Finally, sent them to zabbix
    zs.send_metrics()

if __name__ == '__main__':
    main()
