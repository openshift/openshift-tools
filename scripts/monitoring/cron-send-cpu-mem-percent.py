#!/usr/bin/env python2
'''
   Simple monitoring script to collect per process cpu and mem usage percentages
'''
# vim: expandtab:tabstop=4:shiftwidth=4

# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name

import argparse
import psutil

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='CPU and Memory percentage collector')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('process_str', help='The process cmdline string to match')
    parser.add_argument('zabbix_key_prefix', help='Prefix for the key that will be sent \
        to zabbix with this data, will get a .cpu and .mem suffix')

    return parser.parse_args()

def main():
    """  Main function to run the check """
    argz = parse_args()

    cpu_percent = None
    mem_percent = None
    zagg_data = {}

    for proc in psutil.process_iter():
        try:
            if argz.process_str in proc.name():
                if argz.debug:
                    print proc.cmdline()
                cpu_percent = '{0:.2f}'.format(proc.cpu_percent(interval=0.5))
                mem_percent = '{0:.2f}'.format(proc.memory_percent())
                zagg_data = {'{0}.cpu'.format(argz.zabbix_key_prefix) : cpu_percent,
                             '{0}.mem'.format(argz.zabbix_key_prefix) : mem_percent}
        except psutil.NoSuchProcess:
            pass

    if argz.debug:
        print 'Process ({0}) is using {1} CPU and {2} memory'.format(argz.process_str,
                                                                     cpu_percent,
                                                                     mem_percent)
        print 'Zagg will receive: {0}'.format(zagg_data)

    zgs = ZaggSender(debug=argz.debug)
    zgs.add_zabbix_keys(zagg_keys)
    zgs.send_metrics()

if __name__ == '__main__':
    main()
