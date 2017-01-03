#!/usr/bin/env python2
'''
   Simple monitoring script to collect per process cpu percentage
   and mem usage in bytes (vms or virt and rss)
   usage:
   cron-send-cpu-mem-stats process_name openshift.whatever.zabbix.key
   or
   cron-send-cpu-mem-stats 'something parameter more params' openshift.something.parameter.more.params

   The script will attach .cpu and .mem.{vms|rss} to the end of the zabbix key name for the values

   Future enhancement can be to add multiple instances, that would add pid to the key, but those
   would have to be dynamic items in zabbix
'''
# vim: expandtab:tabstop=4:shiftwidth=4

# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name

import argparse
import psutil
# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='CPU and Memory per process stats collector')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('process_str', help='The process command line string to match')
    parser.add_argument('zabbix_key_prefix', help='Prefix for the key that will be sent \
        to zabbix with this data, will get a .cpu and .mem suffix')

    return parser.parse_args()

def main():
    """  Main function to run the check """
    argz = parse_args()
    proc_parts = argz.process_str.split()

    zagg_data = {}

    for proc in psutil.process_iter():
        try:
            if proc_parts[0] == proc.name():
                proc.dict = proc.as_dict(['cmdline', 'memory_info'])

                cmdline = proc.dict['cmdline']
                if len(proc_parts) > 1 and len(cmdline) > 1:
                    part_count = len(proc_parts[1:])
                    # This call might be confusing, (I know I will be in 2 weeks) so quick explanation:
                    # if the process name matches above, it will check the rest of the strings
                    # against the /proc/<pid>/cmdline contents, order shouldn't matter since all have to match
                    if len(set(proc_parts[1:]).intersection(set(cmdline[1:1+part_count]))) != part_count:
                        continue
                if argz.debug:
                    print cmdline
                cpu_percent = '{0:.2f}'.format(proc.cpu_percent(interval=0.5))
                mem_vms = '{0}'.format(getattr(proc.dict['memory_info'], 'vms'))
                mem_rss = '{0}'.format(getattr(proc.dict['memory_info'], 'rss'))
                zagg_data = {'{0}.cpu'.format(argz.zabbix_key_prefix) : cpu_percent,
                             '{0}.mem.vms'.format(argz.zabbix_key_prefix) : mem_vms,
                             '{0}.mem.rss'.format(argz.zabbix_key_prefix) : mem_rss}
        except psutil.NoSuchProcess:
            pass

    if argz.debug:
        try:
            print 'Process ({0}) is using {1} CPU and {2} {3} memory'.format(argz.process_str,
                                                                             cpu_percent,
                                                                             mem_vms,
                                                                             mem_rss)
            print 'Zagg will receive: {0}'.format(zagg_data)
        except NameError as ex:
            print 'No values: {0}'.format(ex)


    if zagg_data:
        ms = MetricSender(debug=argz.debug)
        ms.add_metric(zagg_data)
        ms.send_metrics()

if __name__ == '__main__':
    main()
