#!/usr/bin/env python
'''
    Quick and dirty create application check for v3
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name
# the to-many-branches

import subprocess
import json
#import time
#import re
#import urllib
#import os

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


def oc_cmd(cmd):
    '''Base command for oc
    '''
    cmds = ['/usr/bin/oc']
    cmds.extend(cmd)
    print ' '.join(cmds)
    proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': '/etc/origin/master/admin.kubeconfig'})
    proc.wait()
    if proc.returncode == 0:
        output = proc.stdout.read()
        return output

    return "Error: %s.  Return: %s" % (proc.returncode, proc.stderr.read())
def get_pv():
    '''Get pv info
    '''
    cmd = ['get', 'pv', '--no-headers', '-o', 'json']
    results = oc_cmd(cmd)
    return json.loads(results)

def get_pv_capacity_total():
    '''Get all the capacity of the total
    '''
    pvinfo = get_pv()
    #pv_capacity_total = sum([int(z['spec']['capacity']['storage'].replace('Gi', '')) for z in pvinfo['items']])
    pv_capacity_total = 0
    for z in pvinfo['items']:
        ca = z['spec']['capacity']['storage']
        pv_capacity_total = pv_capacity_total + int(ca.replace('Gi', ''))
    return pv_capacity_total

def get_pv_capacity_availble():
    '''Get all the capacity avalible
    '''
    pvinfo = get_pv()
    pv_capacity_availble = 0
    for z in pvinfo['items']:
        if z['status']['phase'] == 'Available':
            ca = z['spec']['capacity']['storage']
            pv_capacity_availble = pv_capacity_availble + int(ca.replace('Gi', ''))
    return pv_capacity_availble
def main():
    ''' get the pvspace sum
    '''
    pv_capacity_total = 0
    pv_capacity_availble = 0
    pv_capacity_total = get_pv_capacity_total()
    pv_capacity_availble = get_pv_capacity_availble()
    print 'the total of pv space is : %s' % pv_capacity_total
    print 'the Available of pv space is : %s' % pv_capacity_availble
    zgs = ZaggSender()
    zgs.add_zabbix_keys({'openshift.master.pv.space.total': pv_capacity_total})
    zgs.add_zabbix_keys({'openshift.master.pv.space.availble': pv_capacity_availble})
    zgs.send_metrics()


if __name__ == "__main__":
    main()

