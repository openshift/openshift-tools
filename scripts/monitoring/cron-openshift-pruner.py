#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Prune images/builds/deployments
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
# Disabling invalid-name because pylint doesn't like the naming
# convention we have.
# pylint: disable=invalid-name

import argparse
import base64
import json
import os
import subprocess

SERVICE_ACCOUNT_GROUP = "openshift-infra"
SERVICE_ACCOUNT = "autopruner"
SERVICE_ACCOUNT_TEMPLATE = {"apiVersion": "v1",
                            "kind": "ServiceAccount",
                            "metadata": {"name": SERVICE_ACCOUNT}
                           }

class OpenShiftPrune(object):
    ''' Class to handle pruning of old objects '''
    def __init__(self):
        self.args = None
        self.parse_args()

    def parse_args(self):
        '''Parse the arguments for this script'''

        parser = argparse.ArgumentParser(description="OpenShift object pruner")
        parser.add_argument('-d', '--debug', default=False,
                            action="store_true", help="debug mode")
        parser.add_argument('--image-keep-younger-than', default='24h',
                            help='Ignore images younger than set time')
        parser.add_argument('--image-keep-tag-revisions', default='5',
                            help='Number of image revisions to keep')
        parser.add_argument('--build-keep-younger-than', default='1h',
                            help='Ignore builds younger than set time')
        parser.add_argument('--build-keep-complete', default='2',
                            help='Number of builds to keep')
        parser.add_argument('--build-keep-failed', default='1',
                            help='Number of failed builds to keep')
        parser.add_argument('--deploy-keep-younger-than', default='1h',
                            help='Ignore deployments younger than set time')
        parser.add_argument('--deploy-keep-complete', default='2',
                            help='Number of deployements to keep')
        parser.add_argument('--deploy-keep-failed', default='1',
                            help='Number of failed deployments to keep')
        parser.add_argument('--kube-config', default='/tmp/admin.kubeconfig',
                            help='Kubeconfig creds to use')
        self.args = parser.parse_args()

    def ensure_autopruner_exists(self):
        ''' create autopruning account/perms if it doesn't exist '''

        # user exists?
        cmd = ['oc', 'get', 'serviceaccount', SERVICE_ACCOUNT,
               '-n', SERVICE_ACCOUNT_GROUP,
               '--config', self.args.kube_config]
        rc = subprocess.call(cmd)

        if rc != 0:
            # create service account
            if self.args.debug:
                print "Service account not found. Creating."

            read, write = os.pipe()
            sa_template = json.dumps(SERVICE_ACCOUNT_TEMPLATE)
            os.write(write, sa_template)
            os.close(write)

            cmd = ['oc', 'create', '-n', SERVICE_ACCOUNT_GROUP,
                   '-f', '-',
                   '--config', self.args.kube_config]
            try:
                subprocess.check_call(cmd, stdin=read)
            except subprocess.CalledProcessError:
                print "Error creating service account"
                raise

        # check if autoprune user has pruning perms
        username = "system:serviceaccount:{}:{}".format(SERVICE_ACCOUNT_GROUP,
                                                        SERVICE_ACCOUNT)
        cmd = ['oc', 'get', 'clusterrolebindings', 'system:image-pruner',
               '-o', 'json', '--config', self.args.kube_config]
        output = json.loads(subprocess.check_output(cmd))

        if username not in output['userNames']:
            # grant image pruning
            if self.args.debug:
                print "Granding image pruning perms"

            cmd = ['oadm', 'policy', 'add-cluster-role-to-user',
                   'system:image-pruner', username,
                   '--config', self.args.kube_config]
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                print "Error granting image pruning perms"
                raise

    def get_autopruner_token(self):
        ''' fetch and return the token for the autopruning account '''

        token = None
        self.ensure_autopruner_exists()

        # get token
        cmd = ['oc', 'get', 'serviceaccounts', SERVICE_ACCOUNT,
               '-n', SERVICE_ACCOUNT_GROUP, '-o', 'json',
               '--config', self.args.kube_config]
        output = json.loads(subprocess.check_output(cmd))

        secretname = None
        for secret in output['secrets']:
            if secret['name'].startswith(SERVICE_ACCOUNT + '-token'):
                secretname = secret['name']

        if secretname == None:
            raise Exception("No secret with token info found.")

        cmd = ['oc', 'get', 'secrets', secretname, '-n', SERVICE_ACCOUNT_GROUP,
               '-o', 'json',
               '--config', self.args.kube_config]
        output = json.loads(subprocess.check_output(cmd))
        token = base64.standard_b64decode(output['data']['token'])

        return token

    def prune_images(self):
        ''' call oadm to prune images '''

        token = self.get_autopruner_token()

        cmd = ['oadm', 'prune', 'images',
               '--keep-younger-than', self.args.image_keep_younger_than,
               '--keep-tag-revisions', self.args.image_keep_tag_revisions,
               '--config', self.args.kube_config,
               '--token', token,
               '--confirm']

        output = subprocess.check_output(cmd)
        if self.args.debug:
            print "Prune images output:\n" + output

    def prune_builds(self):
        ''' call oadm to prune builds '''

        cmd = ['oadm', 'prune', 'builds',
               '--keep-complete', self.args.build_keep_complete,
               '--keep-younger-than', self.args.build_keep_younger_than,
               '--keep-failed', self.args.build_keep_failed,
               '--config', self.args.kube_config,
               '--confirm']
        output = subprocess.check_output(cmd)
        if self.args.debug:
            print "Prune build output:\n" + output

    def prune_deployments(self):
        ''' call oadm to prune deployments '''

        cmd = ['oadm', 'prune', 'deployments',
               '--keep-complete', self.args.deploy_keep_complete,
               '--keep-younger-than', self.args.deploy_keep_younger_than,
               '--keep-failed', self.args.deploy_keep_failed,
               '--config', self.args.kube_config,
               '--confirm']

        # can save output and count pruned objects in the future
        output = subprocess.check_output(cmd)
        if self.args.debug:
            print "Prune deployment output:\n" + output

    def main(self):
        ''' Prune images/builds/deployments '''

        self.prune_deployments()
        self.prune_builds()
        self.prune_images()

if __name__ == '__main__':
    OSPruner = OpenShiftPrune()
    OSPruner.main()
