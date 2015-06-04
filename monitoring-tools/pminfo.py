#!/usr/bin/env python
'''
    PMINFOParser perfomant Performance CoPilot pminfo output parser

    This will parse the output of pminfo and return a dictionary of
    the metrics and their values

    This requires that pminfo is installed on the host.
    pminfo will query the localhost host, not another host.

    Examples:

    Collect known values:

    p = PMINFOParser()
    metrics = ['quota.project.files.soft', 'kernel.all.load',
          'kernel.percpu.interrupts.THR', 'kernel.all.cpu.irq.hard']
    metric_dict = p.PPparse(metrics)

    Collect all values:

    p = PMINFOParser()
    metric_dict = p.PPparse()
'''

import subprocess
import re

class PMINFOParser(object):
    '''
        PMINFOParser perfomant Performance CoPilot pminfo output parser
    '''

    def __init__(self):
        self.data = None
        self.metric_regex = None
        self.metric_dict = {}

    def parse(self, metrics=None):
        '''
            docstring placeholder
        '''
        if metrics == None:
            metrics = self.get_pminfo_metrics()

        self.fetch_pminfo_metrics(metrics)
        self.build_metric_regex(metrics)
        self.create_metric_dict()
        self.parse_pminfo()

        return self.metric_dict

    def metric_print(self):
        '''
        Print the metric_dict
        '''
        for key, value in self.metric_dict.items():
            print key
            print "  %s" % value

    def build_metric_regex(self, metrics):
        '''
        build the metric regex
        '''
        joined_metrics = '|'.join(metrics)
        metric_str = '\n(' + joined_metrics + ')\n'
        self.metric_regex = re.compile(metric_str)

    def get_pminfo_metrics(self):
        '''
        get a list of metrics from pminfo.  Return them in a list
        '''
        metrics = self.run_pminfo().strip().split('\n')
        metrics = [s.strip() for s in metrics]

        return  metrics

    def fetch_pminfo_metrics(self, metrics):
        ''' blah
        '''
        self.data = self.run_pminfo(['-f'], metrics)

    def run_pminfo(self, args=None, metric_keys=None):
        '''
            function to run pminfo command with a list of metrics
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
        building a dict

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
            function to parse pminfo and return a dict of metric: metric_value
        '''

        results = {}
        inst_line = re.compile(r'\[\d+ or')

        for metric, metric_value in self.metric_dict.items():
            if 'No value(s) available!' in metric_value:
                results[metric] = None
            elif metric_value.startswith('    value'):
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
                print "PMINFOParser: Uunknown metric key and value: %s : %s" \
                      % (metric, metric_value)

        self.metric_dict = results
