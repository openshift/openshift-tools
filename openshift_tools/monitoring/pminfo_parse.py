#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    PMInfo - Get metrics from Performance CoPilot

    This will parse the output of pminfo and return a dictionary of
    the metrics and their values

    This requires that pminfo is installed on the host.
    pminfo will query the localhost host, not another host.

    NOTE: This does the same thing as pminfo.py, but uses the binary pminfo
    file to call pminfo, and parse the output.  pminfo.py should be used
    instead.

    Examples:

    # Collect known values:

    import pminfo

    metrics = ['quota.project.files.soft', 'kernel.all.load',
          'kernel.percpu.interrupts.THR', 'kernel.all.cpu.irq.hard']

    metric_dict = pminfo.get_metrics(metrics)

    # Collect all values:

    metric_dict = pminfo.get_metrics()
'''

import subprocess
import re

def get_metrics(metrics=None):
    '''
    This function can be used to do the heavy lifting.
    Pass in a list of metrics that will be returned.
    If nothing is passed in, all metric will be returned
    '''
    pminfo = PMInfo()

    metrics = PMInfo.get_pminfo_metrics(metrics)

    pminfo.fetch_pminfo_metrics(metrics)
    pminfo.build_metric_regex(metrics)
    pminfo.create_metric_dict()
    pminfo.parse_pminfo()

    return pminfo.metric_dict

class PMInfo(object):
    '''
    PMINFOParser: Performance CoPilot pminfo output parser
    '''

    def __init__(self):
        self.data = None
        self.metric_regex = None
        self.metric_dict = {}

    def metric_print(self):
        '''
        Print the metric_dict
        '''
        for key, value in self.metric_dict.items():
            print key
            print "  %s" % value

    def build_metric_regex(self, metrics):
        '''
        Build the metric regex
        '''
        joined_metrics = '|'.join(metrics)
        metric_str = '\n(' + joined_metrics + ')\n'
        self.metric_regex = re.compile(metric_str)

    @staticmethod
    def get_pminfo_metrics(metrics):
        '''
        Get a list of metrics from pminfo.  Return them in a list
        '''
        metrics = PMInfo.run_pminfo(metric_keys=metrics).strip().split('\n')
        metrics = [s.strip() for s in metrics]

        return  metrics

    def fetch_pminfo_metrics(self, metrics):
        '''
        This function calls the pminfo function with the -f swith.
        The -f switch 'fetches' the values from pminfo.
        '''
        self.data = PMInfo.run_pminfo(['-f'], metrics)

    @staticmethod
    def run_pminfo(args=None, metric_keys=None):
        '''
        Function to run pminfo command with a list of metrics
        '''
        cmd = ['/usr/bin/pminfo']

        if args:
            cmd += args

        if metric_keys:
            cmd += metric_keys

        process = subprocess.Popen(cmd, stderr=None, stdout=subprocess.PIPE)
        return  process.stdout.read()

    def create_metric_dict(self):
        '''
        Build a metric dict that will be used to collect the metrics and values

        '''
        split_data = re.split(self.metric_regex, self.data)
        exception_list = ['No value(s) available!',
                          'Error: Metric not supported',
                         ]
        for i in range(1, len(split_data), 2):
            if any([exce in split_data[i+1] for exce in exception_list]):
                continue
            self.metric_dict[split_data[i]] = split_data[i+1]

    def parse_pminfo(self):
        '''
        Function to parse pminfo and return a dict of { metric: metric_value(s) }
        '''

        results = {}
        inst_line = re.compile(r'\[\d+ or')

        for metric, metric_value in self.metric_dict.items():
            if metric_value.startswith('    value'):
                metric_value = metric_value.strip()
                value = metric_value.split()[1]
                results[metric] = value
            elif metric_value.startswith('    inst'):
                insts = metric_value.split('    inst ')
                for inst in insts:
                    if not inst:
                        continue
                    metric_subname = None
                    if inst_line.match(inst):
                        metric_subname = inst.split('"')[1].replace(" ", "_")
                    else:
                        metric_subname = inst.split('[')[1].split(']')[0]

                    metric_value = inst.split('] value ')[1].strip()
                    metric_name = metric + "." + metric_subname
                    results[metric_name] = metric_value
            else:
                print "PMINFOParser: Unknown metric key and value: %s : %s" \
                      % (metric, metric_value)

        self.metric_dict = results
