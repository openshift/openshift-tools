#!/usr/bin/python
'''
  Sample pcp for cpu statistics over an interval

  Example:
  ./cron-send-pcp-sample.py -m kernel.all.cpu.idle -m kernel.all.cpu.nice -m kernel.all.cpu.steal \
  -m kernel.all.cpu.sys -m kernel.all.cpu.user -m kernel.all.cpu.wait.total -i 2 -v
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name

import sys
import argparse
import collections
from openshift_tools.monitoring import pminfo
from openshift_tools.monitoring.zagg_sender import ZaggSender

def parse_args():
    '''Parse the arguments for this script'''
    parser = argparse.ArgumentParser(description="Tool to sample pcp metrics")
    parser.add_argument('-m', '--metrics', action="append",
                        help="metrics to send to zabbix")
    parser.add_argument('-i', '--interval', default=10,
                        action="store", help="Sample pcp metrics for $i amount of time. Default: 10")
    parser.add_argument('-c', '--count', default=2,
                        action="store", help="Sample pcp metrics for $i amount of time for $c times. Default: 2")
    parser.add_argument('-d', '--debug', default=False,
                        action="store_true", help="debug mode")
    parser.add_argument('-v', '--verbose', default=False,
                        action="store_true", help="Verbose?")
    parser.add_argument('-t', '--test', default=False,
                        action="store_true", help="Run the script but don't send to zabbix")
    args = parser.parse_args()
    return args, parser


def get_averages(samples):
    ''' Calculate the average of the results of the samples'''
    return {metric: sum(values)/len(values) for (metric, values) in samples.items()}

def main():
    '''Run pminfo against a list of metrics.
       Sample metrics passed in for an amount of time and report data to zabbix
    '''

    args, parser = parse_args()

    if not args.metrics:
        print
        print 'Please specify metrics with -m.'
        print
        parser.print_help()
        sys.exit(1)

    metrics = args.metrics
    interval = int(args.interval)
    count = int(args.count)

    # Gather sampled data
    data = pminfo.get_sampled_data(metrics, interval, count)

    zab_results = collections.defaultdict(list)
    for metric_name, val in data.items():
        if 'kernel' in metric_name:
            for sample in range(len(val)):
                if sample + 1 == len(val):
                    break
                zab_results[metric_name].append(pminfo.calculate_percent_cpu(val[sample], val[sample+1], interval))
        else:
            print 'NOT SUPPORTED: [%s]' % metric_name

        if zab_results.get(metric_name, None) != None and (args.verbose or args.debug):
            print '%s: %.2f' % (metric_name, zab_results[metric_name][-1])

    zab_results = get_averages(zab_results)

    # Send the data to zabbix
    if not args.test:
        zgs = ZaggSender(verbose=args.debug)
        zgs.add_zabbix_keys(zab_results)
        zgs.send_metrics()


if __name__ == '__main__':
    main()
