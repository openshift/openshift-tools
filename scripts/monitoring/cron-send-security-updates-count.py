#!/usr/bin/python
'''
Send a count of pending security updates
'''
#   Copyright 2017 Red Hat Inc.
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
# Purpose:
# Report yum security update count to monitoring system

#pylint: disable=invalid-name

from __future__ import print_function
import argparse
import re
import shutil
import fileinput
import subprocess
from collections import namedtuple
#pylint: disable=import-error
#pylint: enable=import-error
import glob
import yaml
import logging
from configobj import ConfigObj
from openshift_tools.monitoring.metric_sender import MetricSender

ROOT = '/var/local/hostpkg'
LOGFILE = '/var/log/cron-send-security-updates-count.log'

UpdateItem = namedtuple('UpdateItem', 'advisory type package')

class SecurityUpdates(object):
    '''
      This is a check to see how many security updates are pending
    '''
    def __init__(self, options):
        '''SecurityUpdateCount constructor'''
        self.verbose = options.verbose
        self.sec_updates = []
        self.sec_advisory_whitelist = []
        wlfile = '/host/etc/openshift_tools/security_advisory_whitelist.yml'
        try:
            with open(wlfile, 'r') as yaml_file:
                try:
                    whitelist = yaml.safe_load(yaml_file)
                    if 'advisories' in whitelist:
                        self.sec_advisory_whitelist = whitelist['advisories']
                        if self.verbose:
                            print('Whitelisted advisories: {0}'.format(','.join(self.sec_advisory_whitelist)))
                    elif self.verbose:
                        print('No advisories listed in {0}'.format(wlfile))
                except yaml.YAMLError as err:
                    print(err)
        except IOError as err:
            if self.verbose:
                print('Unable to read {0}. Continuing.'.format(wlfile))
                print(err)
            logging.error('Unable to read %s. Continuing.\n%s', wlfile, err)

    #pylint: disable=too-many-branches
    # fixme: pylint doesn't like the nested ifs here
    def get_security_updates(self):
        '''Run yum to get a list of pending security updates'''
        cmd = ['/usr/bin/yum', '--installroot='+ROOT, '-c', ROOT+'/etc/yum.conf',
               '-q', '--security', 'updateinfo', 'list', 'updates']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if self.verbose:
            print('stdout from yum:\n{0}'.format(stdout))
            print('stderr from yum:\n{0}'.format(stderr))
        if proc.returncode != 0:
            self.sec_updates = []
            raise subprocess.CalledProcessError(proc.returncode, subprocess.list2cmdline(cmd), output=stdout+stderr)
        for line in stdout.split('\n'):
            if line and 'Errno' not in line:
                if len(re.split(r'\s+', line)) == 3:
                    self.sec_updates.append(UpdateItem(*re.split(r'\s+', line)))
                else:
                    logging.error('Security update %s looks like error output', line)
            else:
                logging.error('Unable to parse data from security update output: %s\n', line)

        # now sec_updates looks like:
        #     [ UpdateItem(advisory='RHSA-1999:1234', type='Important/Sec.', package='pkgname:1.2.3-0.el7.x86_64'),
        #       UpdateItem(advisory='RHSA-2000:4321', type='Moderate/Sec.', package='somepkt-3:0.19.3-14.el7.x86_64') ]

        for errline in [line for line in stdout.split('\n') if line and 'Errno' in line]:
            if self.verbose:
                print('Error found:', errline)
            logging.error('Error found:' + errline)
        for update in self.sec_updates:
            msg = 'Security update: {0} {1} {2}'.format(update.advisory, update.type, update.package)
            if update.advisory in self.sec_advisory_whitelist:
                if self.verbose:
                    print('Whitelisted {0}'.format(msg))
                logging.info('Whitelisted %s', msg)
            else:
                if self.verbose:
                    print(msg)
                logging.info(msg)

    def get_updates_list(self):
        ''' Return a list of pending security updates (excluding whitelisted items) '''
        return [update for update in self.sec_updates if update.advisory not in self.sec_advisory_whitelist]

    def get_updates_whitelisted_list(self):
        ''' Return a list of whitelisted pending security updates '''
        return [update for update in self.sec_updates if update.advisory in self.sec_advisory_whitelist]

def setup():
    '''
    Make a root dir where yum can be run. Bind mount parts that
    can be used as-is, copy and edit the rest.
    '''
    # we need to edit some config files. Make a copy of all config files.
    shutil.rmtree(ROOT + '/etc/yum', ignore_errors=True)
    shutil.rmtree(ROOT + '/etc/yum.repos.d', ignore_errors=True)
    shutil.copytree('/host/etc/yum', ROOT + '/etc/yum')
    shutil.copytree('/host/etc/yum.repos.d', ROOT + '/etc/yum.repos.d')
    shutil.copyfile('/host/etc/yum.conf', ROOT + '/etc/yum.conf')

    # edit yum.conf
    config = ConfigObj(ROOT + '/etc/yum.conf')
    config['main']['cachedir'] = ROOT + '/var/cache/yum/$basearch/$releasever'
    config['main']['reposdir'] = ROOT + '/etc/yum.repos.d'
    config['main']['pluginconfpath'] = ROOT + '/etc/yum/pluginconf.d'
    config['main']['installroot'] = ROOT
    config['main']['logfile'] = '/var/log/hostpkg.yum.log'
    config.write()

    # edit etc/yum/pluginconf.d/subscription-manager.conf
    config = ConfigObj(ROOT + '/etc/yum/pluginconf.d/subscription-manager.conf')
    # disabled, becuase the host has already created the correct list of repos and if enabled,
    # it'll rewrite our (already correct) etc/yum.repos.d/redhat.repo file with a broken version
    config['main']['enabled'] = '0'
    config.write()

    # edit the repos using fileinput since ConfigParser doesn't support the multi-line format used by yum's baseurl tag
    for line in fileinput.input(glob.glob(ROOT + '/etc/yum.repos.d/*.repo'), inplace=True):
        #NOTE: WARNING: do NOT print anything here. STDOUT is being captured
        #               and written to the repo config file via in-place editing

        # Every time we find a gpgkey, sslcacert, sslclientkey, or sslclientcert tag, we need to see if it refers to
        # a local file, and if so, we'll prepend the path ROOT to it so that yum can find the certs/keys in the right
        # places. For example:
        #    before: sslcacert = https://example.com/ca.pem,file:///etc/pki/example_ca_cert
        #            gpgkey = /etc/pki/rpmkey.gpg
        #    after:  sslcacert = https://example.com/ca.pem,file:///var/local/hostpkg/etc/pki/example_ca_cert
        #            gpgkey = /var/local/hostpkg/etc/pki/rpmkey.gpg
        myre = r'^(?P<field>(?:gpgkey|sslcacert|sslclientkey|sslclientcert)\s*=\s*)(?P<path>.+?)(?P<tail>\s*(?:#.*)?)$'
        match = re.search(myre, line)
        if match:
            # since these directives can be comma seperated, we'll split by comma and then edit each (local) entry
            # then join them back together.
            edited = []
            # pre-pend ROOT to each path
            for path in re.split(r',\s*', match.group('path')):
                match2 = re.search('^(?P<method>(?:[a-z]+://)?)(?P<path>/.*)$', path)
                if match2 and (not match2.group('method') or match2.group('method') == 'file://'):
                    edited.append(match2.group('method') + ROOT + match2.group('path'))
                else:
                    edited.append(path)

            # edit this line of the file
            print(match.group('field') + (','.join(edited)) + match.group('tail'), end='')
        else:
            # keep the original line
            print(line, end='')

def parse_args():
    ''' parse the args from the cli '''
    parser = argparse.ArgumentParser(description='Count needed software updates and send to monitoring system.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Print more information.')

    return parser.parse_args()

def send(values, options):
    ''' Send any passed metrics values '''

    if options.verbose:
        print('Sending values:', values)

    sender = MetricSender()
    for key in values:
        sender.add_metric({key: values[key]})
    sender.send_metrics()

def main():
    ''' This script's main function '''
    logging.basicConfig(format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
                        filename=LOGFILE,
                        level=logging.INFO)
    opts = parse_args()
    setup()

    logging.info('Cleaning yum metadata')
    if opts.verbose:
        print('Cleaning yum metadata')
    cmd = ['/usr/bin/yum', '--installroot='+ROOT, '-c', ROOT+'/etc/yum.conf', '-q', 'clean', 'metadata']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = proc.communicate()
    logging.debug('Metadata cleaned:\n' + stdout)
    if opts.verbose:
        print('Metadata cleaned:\n' + stdout)

    secup = SecurityUpdates(opts)
    # attempt 3 times to get updates.
    attempts = 3
    for attempt in range(0, attempts):
        if opts.verbose:
            print('Making Attept {0} of {1} to fetch list of security updates'.format(attempt+1, attempts))
        try:
            secup.get_security_updates()
            break
        except OSError as err:
            if attempt + 1 == attempts:
                logging.error('Failed all %d attempts to get list of security updates: %s', attempts, err)
                raise
        except subprocess.CalledProcessError as err:
            if attempt + 1 == attempts:
                logging.error('Failed all %d attempts to get list of security updates: %s', attempts, err)
                logging.error('Output of final failure attempt:' + err.output)
                print('Output from failed command:', err.output)
                raise
    values = {}
    values['yum.security.updates'] = len(secup.get_updates_list())
    values['yum.security.updates.skipped'] = len(secup.get_updates_whitelisted_list())
    send(values, opts)

if __name__ == '__main__':
    main()
