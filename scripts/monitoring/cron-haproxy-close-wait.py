#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4

# Disabling invalid-name because pylint doesn't like the naming convention we have.
# pylint: disable=invalid-name
''' Tool to detect haproxy processes in CLOSE_WAIT state, and stop ones
    that have been running more than max_elapsed_time seconds '''

import argparse
import psutil
import time

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

ZABBIX_KEY = "openshift.haproxy.close-wait"

class HAProxy(object):
    ''' wrapper for finding and stopping stuck haproxy processes '''

    def __init__(self):
        ''' constructor '''
        self.args = None
        self.current_time = None

    def dprint(self, msg):
        ''' wrap printing debug messages '''
        if self.args.debug:
            print msg

    def parse_args(self):
        ''' get the max elapsed time '''
        parser = argparse.ArgumentParser(description='haproxy killer')
        parser.add_argument('--max-elapsed-time', default=3600, type=int,
                            help='Max elapsed run time for haproxy in CLOSE_WAIT')
        parser.add_argument('--debug', default=False, action='store_true')
        self.args = parser.parse_args()

    def get_etimes(self, proc):
        ''' Return elapsed time for proc in seconds '''
        return int(self.current_time - proc.create_time())

    def kill(self):
        ''' class entrypoint '''

        self.parse_args()
        self.current_time = time.time()
        haproxy_procs_etimes = {}

        for proc in psutil.process_iter():
            try:
                if proc.name() == 'haproxy':
                    for conn in proc.connections():
                        if conn.status == 'CLOSE_WAIT':
                            elapsed = self.get_etimes(proc)
                            self.dprint("PID: {} elapsed: {}".format(proc.pid, elapsed))
                            if elapsed > self.args.max_elapsed_time:
                                haproxy_procs_etimes[elapsed] = proc.pid

            except psutil.NoSuchProcess:
                pass

        try:
            newest_proc = min(haproxy_procs_etimes.keys())
            haproxy_procs_etimes.pop(newest_proc)
        except ValueError:
            pass

        for proc in haproxy_procs_etimes.values():
            try:
                process = psutil.Process(proc)
                self.dprint("Stopping PID: {}".format(process.pid))
                process.kill()
            except psutil.NoSuchProcess:
                pass

        print "Stopped {} haproxy processes".format(len(haproxy_procs_etimes))

        zgs = ZaggSender()
        zgs.add_zabbix_keys({ZABBIX_KEY : len(haproxy_procs_etimes)})
        zgs.send_metrics()

if __name__ == '__main__':
    hap = HAProxy()
    hap.kill()
