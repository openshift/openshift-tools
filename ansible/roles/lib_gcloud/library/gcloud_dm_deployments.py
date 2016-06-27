#!/usr/bin/env python
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|
'''
   OpenShiftCLI class that wraps the oc commands in a subprocess
'''

import json
import os
import shutil
import subprocess

class GcloudCLIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class GcloudCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self, credentials=None, verbose=False):
        ''' Constructor for OpenshiftCLI '''
        self.credentials = credentials
        self.verbose = verbose

    def _list_deployments(self, simple=True):
        '''list deployments by name '''
        cmd = ['deployment-manager', 'deployments', 'list']
        if simple:
            cmd.append('--simple-list')
        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _delete_deployment(self, dname):
        '''list deployments by name '''
        cmd = ['deployment-manager', 'deployments', 'delete', dname, '-q']
        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _create_deployment(self, dname, config=None, opts=None):
        ''' create a deployment'''
        cmd = ['deployment-manager', 'deployments', 'create', dname]
        if config:
            cmd.extend(['--config=%s' % config])

        if opts:
            for key, val in opts.items():
                cmd.append('--%s=%s' % (key, val))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _update_deployment(self, dname, config=None, opts=None):
        ''' create a deployment'''
        cmd = ['deployment-manager', 'deployments', 'update', dname]
        if config:
            cmd.extend(['--config=%s' % config])

        if opts:
            for key, val in opts.items():
                cmd.append('--%s=%s' % (key, val))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def gcloud_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for gcloud '''
        cmds = ['/home/kwoodson/tmp/google-cloud-sdk/bin/gcloud']

        cmds.extend(cmd)

        rval = {}
        results = ''
        err = None

        if self.verbose:
            print ' '.join(cmds)

        proc = subprocess.Popen(cmds,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env={})

        proc.wait()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        rval = {"returncode": proc.returncode,
                "results": results,
                "cmd": ' '.join(cmds),
               }

        if proc.returncode == 0:
            if output:
                if output_type == 'json':
                    try:
                        rval['results'] = json.loads(stdout)
                    except ValueError as err:
                        if "No JSON object could be decoded" in err.message:
                            err = err.message
                elif output_type == 'raw':
                    rval['results'] = stdout

            if self.verbose:
                print stdout
                print stderr

            if err:
                rval.update({"err": err,
                             "stderr": stderr,
                             "stdout": stdout,
                             "cmd": cmds
                            })

        else:
            rval.update({"stderr": stderr,
                         "stdout": stdout,
                         "results": {},
                        })

        return rval

class Utils(object):
    ''' utilities for openshiftcli modules '''
    @staticmethod
    def cleanup(files):
        '''Clean up on exit '''
        for sfile in files:
            if os.path.exists(sfile):
                if os.path.isdir(sfile):
                    shutil.rmtree(sfile)
                elif os.path.isfile(sfile):
                    os.remove(sfile)


# pylint: disable=too-many-instance-attributes
class GcloudDeploymentManager(GcloudCLI):
    ''' Class to wrap the gcloud deployment manager '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 dname,
                 config=None,
                 opts=None,
                 credentials=None,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(GcloudDeploymentManager, self).__init__()
        self.dname = dname
        self.opts = opts
        self.config = config
        self.credentials = credentials

    def list_deployments(self):
        '''return deployment'''
        results = self._list_deployments()
        if results['returncode'] == 0:
            results['results'] = results['results'].strip().split('\n')

        return results

    def exists(self):
        ''' return whether a deployment exists '''
        deployments = self.list_deployments()
        if deployments['returncode'] != 0:
            raise GcloudCLIError('Something went wrong.  Results: %s' % deployments['stderr'])
        return self.dname in deployments['results']


    def delete(self):
        '''delete a deployment'''
        return self._delete_deployment(self.dname)

    def create_deployment(self):
        '''create a deployment'''
        return self._create_deployment(self.dname, self.config, self.opts)

    def update_deployment(self):
        '''update a deployment'''
        return self._update_deployment(self.dname, self.config, self.opts)

# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud deployment-manager deployments '''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str'),
            config=dict(default=None, type='str'),
            opts=dict(default=None, type='dict'),
        ),
        supports_check_mode=True,
    )
    gconfig = GcloudDeploymentManager(module.params['name'],
                                      module.params['config'],
                                      module.params['opts'])

    state = module.params['state']

    api_rval = gconfig.list_deployments()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if gconfig.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = gconfig.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not gconfig.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = gconfig.create_deployment()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        api_rval = gconfig.update_deployment()

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=True, results=api_rval, state="present")


    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudDeploymentManager('optestgcp')
#    print gcloud.list_deployments()


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
