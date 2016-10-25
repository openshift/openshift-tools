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
import atexit
import shutil
import string
import random
import yaml
import subprocess

# pylint: disable=bare-except
def cleanup_file(inc_file):
    ''' clean up '''
    try:
        os.unlink(inc_file)
    except:
        pass

class OCUtil(object):
    ''' Wrapper for interfacing with OpenShift 'oc' utility '''

    def __init__(self, namespace='default', config_file='/tmp/admin.kubeconfig',
                 verbose=False, logger=None):
        '''
        Take initial values for running 'oc'
        Ensure to set non-default namespace if that is what is desired
        '''
        self.namespace = namespace
        self.config_file = config_file
        self.verbose = verbose
        self.copy_kubeconfig()
        self.logger = logger

    def copy_kubeconfig(self):
        ''' make a copy of the kubeconfig '''

        file_name = os.path.join(
            '/tmp',
            ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        )
        shutil.copy(self.config_file, file_name)
        atexit.register(cleanup_file, file_name)

        self.config_file = file_name

    def _run_cmd(self, cmd, baseCmd='oc', ):
        ''' Actually execute the command '''
        cmd = " ".join([
            baseCmd,
            '--config', self.config_file,
            '-n', self.namespace,
            cmd,
        ])

        if self.logger:
            self.logger.debug("ocutil._run_cmd( {} )".format(cmd))

        cmd = shlex.split(cmd)

        if self.verbose:
            print "Running command: {}".format(str(cmd))

        return subprocess.check_output(cmd)

    def _run_cmd_yaml(self, cmd, baseCmd='oc', yamlCmd='-o yaml', ):
        return yaml.safe_load(self._run_cmd(
            " ".join([cmd, yamlCmd]),
            baseCmd=baseCmd,
        ))

    def run_user_cmd(self, cmd, baseCmd='oc', ):
        ''' Runs a custom user command '''
        return self._run_cmd(
            cmd,
            baseCmd=baseCmd,
        )

    def run_user_cmd_yaml(self, cmd, baseCmd='oc', yamlCmd='-o yaml', ):
        ''' Runs a custom user command and expects yaml '''
        return self._run_cmd_yaml(
            cmd,
            baseCmd=baseCmd,
            yamlCmd=yamlCmd,
        )

    def get_secrets(self, name):
        ''' Get secrets from object 'name' '''
        return self._run_cmd_yaml("get secrets {}".format(name))

    def get_endpoint(self, name):
        ''' Get endpoint details '''
        return self._run_cmd_yaml("get endpoints {}".format(name))

    def get_service(self, name):
        ''' Get service details '''
        return self._run_cmd_yaml("get service {}".format(name))

    def get_dc(self, name):
        ''' Get deployment config details '''
        return self._run_cmd_yaml("get dc {}".format(name))

    def get_route(self, name):
        ''' Get routes details '''
        return self._run_cmd_yaml("get route {}".format(name))

    def get_pods(self):
        ''' Get all the pods in the namespace '''
        return self._run_cmd_yaml("get pods")

    def get_projects(self):
        ''' Get all projects in the cluster '''
        return self._run_cmd_yaml("get projects")

    def get_nodes(self):
        ''' Get all the nodes in the cluster '''
        return self._run_cmd_yaml("get nodes")

    def get_log(self, name):
        ''' Gets the log for the specified container '''
        return self._run_cmd("logs {}".format(name))
