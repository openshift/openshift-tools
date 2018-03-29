#!/usr/bin/env python
'''
  Send url checks to Zagg
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2018 Red Hat Inc.
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
# oso modules won't be available to pylint in Jenkins
#pylint: disable=import-error

import argparse
import sys
import logging
from logging.handlers import RotatingFileHandler
import requests
import urllib3
import yaml
from openshift_tools.monitoring.metric_sender import MetricSender

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logFile = '/var/log/cron-send-url-check.log'

logRFH = RotatingFileHandler(logFile, mode='a', maxBytes=2*1024*1024, backupCount=5, delay=0)
logRFH.setFormatter(logFormatter)
logRFH.setLevel(logging.INFO)
logger.addHandler(logRFH)
logConsole = logging.StreamHandler()
logConsole.setLevel(logging.WARNING)
logger.addHandler(logConsole)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UrlCheck(object):
    """Checks for an url"""

    def __init__(self):
        self.args = None
        self.metrics = None # metric sender
        self.config = None
        self.default_config = '/etc/openshift_tools/urlchecks.yml'
        self.parse_args()
        if self.args.verbose:
            logConsole.setLevel(logging.INFO)
        if self.args.debug:
            logConsole.setLevel(logging.DEBUG)

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift url check sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Collect stats, but no report to zabbix')
        parser.add_argument('-c', '--configfile', default=self.default_config,
                            help="Config file that contains urls to check, defaults to urlchecks.yml")

        self.args = parser.parse_args()

    @staticmethod
    def check_url(url):
        ''' Connect to URL and check if you get http 200 back '''
        logger.debug('Running the check against %s', url)
        try:
            returncode = requests.get(url, verify=False).status_code
            logger.debug("return code %s", returncode)
            return bool(returncode == 200)
        except requests.exceptions.RequestException:
            logger.error("URL check failed. ")
            return False

    def run(self):
        """Main function to run the check"""
        logging.info('Starting url checker...')

        try:
            with open(self.args.configfile, 'r') as configfile:
                self.config = yaml.load(configfile)
                logging.debug('Loaded config file: %s', self.config)
        except IOError:
            logging.error('There was a problem opening the config file. Exiting.')
            sys.exit(1)

        return_data = {}
        self.metrics = MetricSender(verbose=self.args.verbose, debug=self.args.debug)

        for itemtocheck in self.config['urls_to_check']:
            if self.check_url(itemtocheck['url']):
                return_data[itemtocheck['zab_key']] = 1
            else:
                return_data[itemtocheck['zab_key']] = 0

        logger.debug('return_data before adding to sender: %s', return_data)
        self.metrics.add_metric(return_data)

        logger.info('self metrics before sending to zabbix %s',
                    self.metrics.active_senders[0].unique_metrics)
        if self.args.dry_run:
            self.metrics.print_unique_metrics()
        else:
            self.metrics.send_metrics()

if __name__ == '__main__':
    uc = UrlCheck()
    uc.run()
