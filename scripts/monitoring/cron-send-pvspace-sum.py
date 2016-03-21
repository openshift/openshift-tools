#!/usr/bin/env python
'''
    Quick and dirty create application check for v3
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name
# the to-many-branches

import subprocess
#import sys
#import os

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


def oc_cmd(cmd):
    '''Base command for oc
    '''
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                            env={'KUBECONFIG': '/etc/origin/master/admin.kubeconfig'}, shell=True)
    proc.wait()
    if proc.returncode == 0:
        output = proc.stdout.read()
        return output

    return "Error: %s.  Return: %s" % (proc.returncode, proc.stderr.read())


def main():
    ''' get the pvspace sum
    '''

    sum_pv = oc_cmd("oc get pv |awk '{print $3}'|sed 's/Gi//g'|awk '{s+=$1} END {print s}'")
    print 'the total of pv space is : %s' % sum_pv
    zgs = ZaggSender()
    zgs.add_zabbix_keys({'openshift.master.pv.space.total': sum_pv})
    zgs.send_metrics()


if __name__ == "__main__":
    main()

