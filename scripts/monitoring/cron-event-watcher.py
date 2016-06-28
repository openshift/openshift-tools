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
from openshift_tools.monitoring.zagg_sender import ZaggSender
import json
from Queue import Queue
import re
import subprocess
import threading
import time

ZBX_KEY = "openshift.master.cluster.event."

#pylint: disable=too-few-public-methods
class OpenshiftEventConsumer(object):
    ''' Submits events to Zabbix '''

    def __init__(self, args, queue):
        self.queue = queue
        self.args = args

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
            for event_type in self.args.watch_for:
                event_counts[event_type] = 0

            for event in event_list:
                event_counts[event] += 1

            if self.args.verbose or self.args.dry_run:
                print "Got events: " + str(event_counts)

            if not self.args.dry_run:
                zagg_sender = ZaggSender(verbose=self.args.verbose,
                                         debug=self.args.debug)
                for event in event_counts.keys():
                    key = ZBX_KEY + event.lower()
                    zagg_sender.add_zabbix_keys({key: event_counts[event]})
                zagg_sender.send_metrics()

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
        ''' create list of events/reasons to watch for '''
        self.args.watch_for = self.args.watch_for.split(',')

    def parse_args(self):
        ''' parse the args from the cli '''

        parser = argparse.ArgumentParser(description='OpenShift event watcher')
        parser.add_argument('--config', default='/etc/origin/master/admin.kubeconfig',
                            help='Location of OpenShift kubeconfig file')
        parser.add_argument('-v', '--verbose', action='store_true',
                            default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true',
                            default=None, help='Debug?')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Do not send results to Zabbix')
        parser.add_argument('--watch-for', required=True,
                            help='Comma-separated list of case-sensitive events ' + \
                                 'to match.')
        parser.add_argument('--reporting-period', default=60, type=int,
                            help='How many seconds between each reporting period')

        self.args = parser.parse_args()

        self.watch_list_setup()

    def event_watch_loop(self):
        ''' Loop to read/process OpenShift events '''

        while True:
            popen = subprocess.Popen(['oc', 'get', 'events', '--all-namespaces',
                                      '-o', 'json', '--config',
                                      self.args.config, '--watch-only'],
                                     bufsize=1, stdout=subprocess.PIPE)

            json_str = ""
            print "Watching for events: " + str(self.args.watch_for)

            for line in iter(popen.stdout.readline, b''):
                # concatenate each line of output into a single
                # string holding a json-formatted object
                json_str = json_str + ' ' + line.rstrip()

                if re.match("}", line): # '}' signals end of json object
                    json_obj = json.loads(json_str)
                    if self.args.verbose or self.args.debug:
                        print "Event type: " + json_obj['reason']

                    if self.args.debug:
                        print "Received event: "
                        print json.dumps(json_obj, sort_keys=True, indent=4)

                    if json_obj['reason'] in self.args.watch_for:
                        if self.args.verbose:
                            print "Matched event: " + json_obj['reason']
                        self.queue.put(json_obj['reason'])
                    json_str = ""

            # Never should get here

if __name__ == '__main__':
    event_queue = Queue()

    OEW = OpenshiftEventWatcher(event_queue)
    watch_thread = threading.Thread(target=OEW.run)
    watch_thread.start()

    OEC = OpenshiftEventConsumer(OEW.args, event_queue)
    event_consumer = threading.Thread(target=OEC.run)
    event_consumer.start()
