#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Interface to OpenShift oc command
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
import subprocess

class OCUtil(object):
    ''' Wrapper for interfacing with OpenShift 'oc' utility '''

    def __init__(self, namespace='default', config_file='/etc/origin/master/admin.kubeconfig', verbose=False):
        '''
        Take initial values for running 'oc'
        Ensure to set non-default namespace if that is what is desired
        '''

        self.namespace = namespace
        self.config_file = config_file

        self.verbose = verbose

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

    def get_secrets(self, name):
        ''' Get secrets from object 'name' '''


        secrets_cmd = "oc get secrets {} -n{} -o yaml".format(name, self.namespace)
        secrets_yaml = self._run_cmd(secrets_cmd)

        return secrets_yaml

    def get_endpoint(self, name):
        ''' Get endpoint details '''

        endpoint_cmd = "oc get endpoints {} -n{} -o yaml".format(name, self.namespace)
        endpoint_yaml = self._run_cmd(endpoint_cmd)

        return endpoint_yaml

    def get_service(self, name):
        ''' Get service details '''

        service_cmd = "oc get service {} -n{} -o yaml".format(name, self.namespace)
        service_yaml = self._run_cmd(service_cmd)

        return service_yaml
