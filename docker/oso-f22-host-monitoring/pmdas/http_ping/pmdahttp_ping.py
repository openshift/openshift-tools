#!/usr/bin/env python2
'''
Performance Metrics Domain Agent exporting an http status code
'''
#
# Copyright (c) 2014-2015 Red Hat.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#

# Pylint has libraries that are not installed on the build bot.
# pylint: disable=import-error
import cpmapi as c_api
from pcp.pmapi import pmUnits
from pcp.pmda import PMDA, pmdaMetric
import threading

# PCP is built for python3.  This fails under the bot in python2.7
# pylint: disable=no-name-in-module
import urllib.request as urllib

TIMEOUT = 10

# This class only needs run but could expand in the future
# pylint: disable=too-few-public-methods
class FetchURL(object):
    ''' External threaded class to fetch a url '''
    def __init__(self, url, pmdaObject=None, timeout=TIMEOUT):
        self.url = url
        self.pmda = pmdaObject
        self.timeout = timeout
        self.code = None
        self.resp = None

    def run(self):
        ''' Run method that fetches URL in separate thread
        '''
        def fetch_url_thread():
            ''' Fetch the url in a separate thread
            '''
            self.resp = urllib.urlopen(self.url)
        thread = threading.Thread(target=fetch_url_thread)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            thread.join()
            if self.pmda:
                self.pmda.log('Timeout when fetching url (%s)' % self.url)
        self.code = self.resp.getcode()

class HttpPing(PMDA):
    '''
    Performance Metrics Domain Agent exporting for services.
    Install it and make basic use of it if you use os_services, as follows:

    # $PCP_PMDAS_DIR/os_services/Install
    $ pminfo -fmdtT os_services
    '''

    def ping_fetch(self):
        '''
        Called once per PCP "fetch" PDU from pmcd(1)
        Fetch a url
        '''
        fetch = FetchURL('http://www.google.com', self)
        fetch.run()
        self.values['ping'] = fetch.code

    def ping_fetch_callback(self, cluster, item, inst):
        '''
        Main fetch callback - looks up value associated with requested PMID
        '''
        #self.log("fetch callback for %d.%d[%d]" % (cluster, item, inst))
        #self.log("PM_IN_NULL:  %d" % (c_api.PM_IN_NULL))
        if inst != c_api.PM_IN_NULL:
            return [c_api.PM_ERR_INST, 0]
        elif cluster != 0:
            return [c_api.PM_ERR_PMID, 0]
        #if item >= 0 and item < self.nmetrics:
            #return [c_api.PM_ERR_AGAIN, 0]

        if item == 0:
            return [self.values.get('ping', 0), 1]
        return [c_api.PM_ERR_PMID, 0]


    def setup_ping_metrics(self, name):
        '''
        Setup the metric table - ensure a values hash entry is setup for
        each metric; that way we don't need to worry about KeyErrors in
        the fetch callback routine (e.g. if the kernel interface changes).
        '''
        self.values['ping'] = 0
        # This class inherits from PDMA which includes these methods
        # pylint: disable=no-member
        self.add_metric(name + '.ping',
                        pmdaMetric(self.pmid(0, 0),
                                   c_api.PM_TYPE_U32,
                                   c_api.PM_INDOM_NULL,
                                   c_api.PM_SEM_INSTANT,
                                   pmUnits(0, 0, 0, 0, 0, 0)),
                        'Http ping to google.com http status codde')

    def __init__(self, name, domain):
        PMDA.__init__(self, name, domain)

        self.values = {}
        self.setup_ping_metrics(name)
        self.nmetrics = len(self.values)

        # This class inherits from PDMA which includes these methods
        # pylint: disable=no-member
        self.set_fetch(self.ping_fetch)
        self.set_fetch_callback(self.ping_fetch_callback)


if __name__ == '__main__':
    # This class inherits from PDMA which includes the run method
    # pylint: disable=no-member
    HttpPing('http_ping', 301).run()
