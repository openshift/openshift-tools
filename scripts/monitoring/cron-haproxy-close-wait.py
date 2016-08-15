#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4

# Disabling invalid-name because pylint doesn't like the naming convention we have.
# pylint: disable=invalid-name
''' Tool to detect haproxy processes that have been running longer than
    the most recent haproxy process and have connection in CLOSE_WAIT state
    and stop them '''

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
        ''' get user args '''
        parser = argparse.ArgumentParser(description='haproxy killer')
        parser.add_argument('--debug', default=False, action='store_true')
        self.args = parser.parse_args()

    def get_etimes(self, proc):
        ''' Return elapsed time for proc in seconds '''
        return int(self.current_time - proc.create_time())

    def get_all_haproxy_procs(self):
        ''' build dict of elapsed times mapped to PIDs for all
            haproxy processes running '''
        all_procs = {}
        for proc in psutil.process_iter():
            try:
                if proc.name() == 'haproxy':
                    elapsed = self.get_etimes(proc)
                    all_procs[elapsed] = proc.pid

            except psutil.NoSuchProcess:
                pass

        return all_procs

    def kill(self):
        ''' class entrypoint '''

        self.parse_args()
        self.current_time = time.time()

        haproxy_procs_etimes = self.get_all_haproxy_procs()

        # identify most recent haproxy process
        # and remove it from list of haproxy processes
        try:
            youngest_etimes = min(haproxy_procs_etimes.keys())
            youngest_pid = haproxy_procs_etimes[youngest_etimes]
            self.dprint("Youngest haproxy PID: {}".format(youngest_pid))
            haproxy_procs_etimes.pop(youngest_etimes)
        except ValueError:
            pass

        # find processes that have connections only in 'CLOSE-WAIT' state
        kill_list = []
        for proc in haproxy_procs_etimes.values():
            try:
                only_close_wait = True
                process = psutil.Process(proc)
                for conn in process.connections():
                    if conn.status != 'CLOSE_WAIT':
                        only_close_wait = False
                        break
                if only_close_wait:
                    self.dprint("PID: {} marked for removal".format(proc))
                    kill_list.append(proc)
            except psutil.NoSuchProcess:
                pass

        # stop processes on the kill_list
        kill_count = 0
        for proc in kill_list:
            try:
                process = psutil.Process(proc)
                self.dprint("Stopping PID: {}".format(process.pid))
                process.kill()
                kill_count += 1
            except psutil.NoSuchProcess:
                pass

        print "Stopped {} haproxy processes".format(kill_count)

        zgs = ZaggSender()
        zgs.add_zabbix_keys({ZABBIX_KEY : kill_count})
        zgs.send_metrics()

if __name__ == '__main__':
    hap = HAProxy()
    hap.kill()
