#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Process OpenShift event stream
'''
#
#   Copyright 2016 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
# pylint flaggs import errors, as the bot doesn't know out openshift-tools libs
#pylint: disable=import-error

import argparse
from openshift_tools.monitoring.metric_sender import MetricSender
import json
from Queue import Queue
import re
import subprocess
import threading
import time
import yaml

#pylint: disable=too-few-public-methods
class OpenshiftEventConsumer(object):
    ''' Submits events to Zabbix '''

    def __init__(self, args, queue, zbx_keys):
        self.queue = queue
        self.args = args
        self.zbx_keys = zbx_keys

    def run(self):
        ''' main function '''

        while True:
            event_list = []
            while not self.queue.empty():
                event = self.queue.get()
                if self.args.debug:
                    print "Processing event: {}".format(str(event))
                event_list.append(event)

            # initialize event counts so that we send '0' events
            # in the case where no events were received
            event_counts = {}
            for zbx_key in self.zbx_keys:
                event_counts[zbx_key] = 0

            # add up each distinct event
            for event in event_list:
                event_counts[event] += 1

            if self.args.verbose or self.args.dry_run:
                print "Got events: " + str(event_counts)

            if not self.args.dry_run:
                metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)
                for event, count in event_counts.iteritems():
                    metric_sender.add_metric({event: count})
                metric_sender.send_metrics()

            time.sleep(self.args.reporting_period)

        # Never should get here

class OpenshiftEventWatcher(object):
    ''' Watches OpenShift event stream '''

    def __init__(self, queue):
        self.args = None
        self.queue = queue
        self.parse_args()

    def run(self):
        '''  Main function '''

        self.event_watch_loop()

    def watch_list_setup(self):
        ''' create dict of events/reasons to watch for
            plus a regex to further filter events'''
        with open(self.args.config, 'r') as config:
            self.args.watch_for = yaml.load(config)['event_watcher_config']

    def parse_args(self):
        ''' parse the args from the cli '''

        parser = argparse.ArgumentParser(description='OpenShift event watcher')
        parser.add_argument('--kubeconfig', default='/etc/origin/master/admin.kubeconfig',
                            help='Location of OpenShift kubeconfig file')
        parser.add_argument('--config', default='/container_setup/monitoring-config.yml',
                            help='Config file for event watcher script')
        parser.add_argument('-v', '--verbose', action='store_true',
                            default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true',
                            default=None, help='Debug?')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Do not send results to Zabbix')
        parser.add_argument('--reporting-period', default=60, type=int,
                            help='How many seconds between each reporting period')

        self.args = parser.parse_args()

        self.watch_list_setup()

    def check_event(self, event):
        ''' If an event is something we're looking for
            return the key it should be reported as '''

        # Most events aren't something we will care about
        # so catch that case and return early
        if event['reason'] not in self.args.watch_for.keys():
            return None

        regex_list = self.args.watch_for[event['reason']]
        for regex in regex_list:
            if re.search(regex['pattern'], event['message']):
                return regex['zbx_key']

        # If we made it here, then there was no regex match
        # so the event is not something we will report to zabbix
        return None

    def get_zbx_keys(self):
        ''' return list of zbx keys config file says to report on '''

        zbx_keys = []
        for _, regex_list in self.args.watch_for.iteritems():
            for regex in regex_list:
                zbx_keys.append(regex['zbx_key'])

        return zbx_keys

    def event_watch_loop(self):
        ''' Loop to read/process OpenShift events '''

        while True:
            popen = subprocess.Popen(['oc', 'get', 'events', '--all-namespaces',
                                      '-o', 'json', '--config',
                                      self.args.kubeconfig, '--watch-only'],
                                     bufsize=1, stdout=subprocess.PIPE)

            json_str = ""
            print "Watching for events: " + str(self.args.watch_for)

            for line in iter(popen.stdout.readline, b''):
                # concatenate each line of output into a single
                # string holding a json-formatted object
                json_str = json_str + ' ' + line.rstrip()

                if re.match("}", line): # '}' signals end of json object
                    json_obj = json.loads(json_str)
                    if self.args.debug:
                        print "Event type: " + json_obj['reason']
                        print json.dumps(json_obj, sort_keys=True, indent=4)

                    result = self.check_event(json_obj)
                    if result:
                        if self.args.verbose:
                            print "Matched event: " + json_obj['reason'] + \
                                  " " + json_obj['message']
                        self.queue.put(result)
                    json_str = ""

            # Never should get here

if __name__ == '__main__':
    event_queue = Queue()

    OEW = OpenshiftEventWatcher(event_queue)
    zbx_key_list = OEW.get_zbx_keys()
    watch_thread = threading.Thread(target=OEW.run)
    watch_thread.start()

    OEC = OpenshiftEventConsumer(OEW.args, event_queue, zbx_key_list)
    event_consumer = threading.Thread(target=OEC.run)
    event_consumer.start()
