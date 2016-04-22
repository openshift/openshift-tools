#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Interface to OpenShift oadm command
'''
#
#   Copyright 2015 Red Hat Inc.
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
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

import os
import shlex
import atexit
import shutil
import string
import random
import subprocess

# pylint: disable=bare-except
def cleanup_file(inc_file):
    ''' clean up '''
    try:
        os.unlink(inc_file)
    except:
        pass

class OadmUtil(object):
    ''' Wrapper for interfacing with OpenShift 'oadm' utility '''

    def __init__(self, namespace='default', config_file='/tmp/admin.kubeconfig', verbose=False):
        '''
        Take initial values for running 'oadm'
        Ensure to set non-default namespace if that is what is desired
        '''
        self.namespace = namespace
        self.config_file = config_file
        self.verbose = verbose
        self.copy_kubeconfig()

    def copy_kubeconfig(self):
        ''' make a copy of the kubeconfig '''

        file_name = os.path.join('/tmp',
                                 ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)))
        shutil.copy(self.config_file, file_name)
        atexit.register(cleanup_file, file_name)

        self.config_file = file_name

    def _run_cmd(self, cmd):
        ''' Actually execute the command '''

        cmd = cmd + ' --config ' + self.config_file
        cmd = shlex.split(cmd)
        if self.verbose:
            print "Running command: {}".format(str(cmd))

        results = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   env={'PATH': os.environ["PATH"]})
        results.wait()
        if results.returncode != 0:
            raise Exception("Non-zero exit on command: {}".format(str(cmd)))

        return results.stdout.read()

    def get_version(self):
        ''' Get version of openshift/kubernetes '''

        version_cmd = "oadm version "
        version_output = self._run_cmd(version_cmd)

        return version_output

