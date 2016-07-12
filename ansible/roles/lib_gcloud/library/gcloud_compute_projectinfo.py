#!/usr/bin/env python
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|

'''
   GcloudCLI class that wraps the oc commands in a subprocess
'''

import string
import random
import json
import os
import yaml
import shutil
import subprocess
import atexit

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

    def _create_image(self, image_name, image_info):
        '''create an image name'''
        cmd = ['compute', 'images', 'create', image_name]
        for key, val in image_info.items():
            if val:
                cmd.extend(['--%s' % key, val])

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _delete_image(self, image_name):
        '''delete image by name '''
        cmd = ['compute', 'images', 'delete', image_name]
        if image_name:
            cmd.extend(['describe', image_name])
        else:
            cmd.append('list')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_images(self, image_name=None):
        '''list images.
           if name is supplied perform a describe and return
        '''
        cmd = ['compute', 'images']
        if image_name:
            cmd.extend(['describe', image_name])
        else:
            cmd.append('list')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

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
            if isinstance(config, dict):
                config = Utils.create_file(dname, config)

            if isinstance(config, str) and os.path.exists(config):
                cmd.extend(['--config=%s' % config])

        if opts:
            for key, val in opts.items():
                cmd.append('--%s=%s' % (key, val))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _update_deployment(self, dname, config=None, opts=None):
        ''' create a deployment'''
        cmd = ['deployment-manager', 'deployments', 'update', dname]
        if config:
            if isinstance(config, dict):
                config = Utils.create_file(dname, config)

            if isinstance(config, str) and os.path.exists(config):
                cmd.extend(['--config=%s' % config])

        if opts:
            for key, val in opts.items():
                cmd.append('--%s=%s' % (key, val))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_manifests(self, deployment, mname=None):
        ''' list manifests
            if a name is specified then perform a describe
        '''
        cmd = ['deployment-manager', 'manifests', '--deployment', deployment]
        if mname:
            cmd.extend(['describe', mname])
        else:
            cmd.append('list')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _delete_address(self, aname):
        ''' list addresses
            if a name is specified then perform a describe
        '''
        cmd = ['compute', 'addresses', 'delete', aname]

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_addresses(self, aname=None):
        ''' list addresses
            if a name is specified then perform a describe
        '''
        cmd = ['compute', 'addresses']
        if aname:
            cmd.extend(['describe', aname])
        else:
            cmd.append('list')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _create_address(self, address_name, address_info, address=None, isglobal=False):
        ''' create a deployment'''
        cmd = ['compute', 'addresses', 'create', address_name]

        if address:
            cmd.append(address)

        if isglobal:
            cmd.append('--global')

        for key, val in address_info.items():
            if val:
                cmd.extend(['--%s' % key, val])

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_metadata(self):
        '''create metadata'''
        cmd = ['compute', 'project-info', 'describe']

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _delete_metadata(self, keys, remove_all=False):
        '''create metadata'''
        cmd = ['compute', 'project-info', 'remove-metadata']

        if remove_all:
            cmd.append('--all')

        else:
            cmd.append('--keys')
            cmd.append(','.join(keys))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _create_metadata(self, metadata=None, metadata_from_file=None):
        '''create metadata'''
        cmd = ['compute', 'project-info', 'add-metadata']

        data = None

        if metadata_from_file:
            cmd.append('--metadata-from-file')
            data = metadata_from_file
        else:
            cmd.append('--metadata')
            data = metadata

        cmd.append(','.join(['%s=%s' % (key, val) for key, val in data.items()]))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def gcloud_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for gcloud '''
        cmds = ['/usr/bin/gcloud']

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

################################################################################
# utilities and helpers for generation
################################################################################
class Utils(object):
    ''' utilities for openshiftcli modules '''

    COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

    @staticmethod
    def create_file(rname, data, ftype='yaml'):
        ''' create a file in tmp with name and contents'''
        path = os.path.join('/tmp', rname)
        with open(path, 'w') as fds:
            if ftype == 'yaml':
                fds.write(yaml.safe_dump(data, default_flow_style=False))

            elif ftype == 'json':
                fds.write(json.dumps(data))
            else:
                fds.write(data)

        # Register cleanup when module is done
        atexit.register(Utils.cleanup, [path])
        return path

    @staticmethod
    def global_compute_url(project, collection, rname):
        '''build the global compute url for a resource'''
        return ''.join([Utils.COMPUTE_URL_BASE, 'projects/', project, '/global/', collection, '/', rname])

    @staticmethod
    def zonal_compute_url(project, zone, collection, rname):
        '''build the zone compute url for a resource'''
        return ''.join([Utils.COMPUTE_URL_BASE, 'projects/', project, '/zones/', zone, '/', collection, '/', rname])

    @staticmethod
    def generate_random_name(size):
        '''generate a random string of lowercase and digits the length of size'''
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))


    @staticmethod
    def cleanup(files):
        '''Clean up on exit '''
        for sfile in files:
            if os.path.exists(sfile):
                if os.path.isdir(sfile):
                    shutil.rmtree(sfile)
                elif os.path.isfile(sfile):
                    os.remove(sfile)


class GcloudComputeProjectInfoError(Exception):
    '''exception class for projectinfo'''
    pass

# pylint: disable=too-many-instance-attributes
class GcloudComputeProjectInfo(GcloudCLI):
    ''' Class to wrap the gcloud compute projectinfo command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 metadata=None,
                 metadata_from_file=None,
                 remove_keys=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeProjectInfo, self).__init__()
        self._metadata = metadata
        self.metadata_from_file = metadata_from_file
        self.remove_keys = remove_keys
        self._existing_metadata = None
        self.verbose = verbose

    @property
    def metadata(self):
        '''property for existing metadata'''
        return self._metadata

    @property
    def existing_metadata(self):
        '''property for existing metadata'''
        if self._existing_metadata == None:
            self._existing_metadata = []
            metadata = self.list_metadata()
            metadata = metadata['results']['commonInstanceMetadata']
            if metadata.has_key('items'):
                self._existing_metadata = metadata['items']

        return self._existing_metadata

    def list_metadata(self):
        '''return metatadata'''
        results = self._list_metadata()
        if results['returncode'] == 0:
            results['results'] = yaml.load(results['results'])

        return results

    def exists(self):
        ''' return whether the metadata that we are removing exists '''
        # currently we aren't opening up files for comparison so always return False
        if self.metadata_from_file:
            return False

        for key, val in self.metadata.items():
            for data in self.existing_metadata:
                if key == 'sshKeys' and data['key'] == key:
                    ssh_keys = {}
                    # get all the users and their public keys out of the project
                    for user_pub_key in data['value'].strip().split('\n'):
                        col_index = user_pub_key.find(':')
                        user = user_pub_key[:col_index]
                        pub_key = user_pub_key[col_index+1:]
                        ssh_keys[user] = pub_key
                    # compare the users that were passed in to see if we need to update
                    for inc_user, inc_pub_key in val.items():
                        if not ssh_keys.has_key(inc_user) or ssh_keys[inc_user] != inc_pub_key:
                            return False
                    # matched all ssh keys
                    break

                elif data['key'] == str(key) and str(data['value']) == str(val):
                    break
            else:
                return False

        return True

    def keys_exist(self):
        ''' return whether the keys exist in the metadata'''
        for key in self.remove_keys:
            for mdata in self.existing_metadata:
                if key == mdata['key']:
                    break

            else:
                # NOT FOUND
                return False

        return True

    def needs_update(self):
        ''' return whether an we need to update '''
        # compare incoming values with metadata returned
        # for each key in user supplied check against returned data
        return not self.exists()

    def delete_metadata(self, remove_all=False):
        ''' attempt to remove metadata '''
        return self._delete_metadata(self.remove_keys, remove_all=remove_all)

    def create_metadata(self):
        '''create an metadata'''
        results = None
        if self.metadata and self.metadata.has_key('sshKeys'):
            # create a file and pass it to create
            ssh_strings = ["%s:%s" % (user, pub_key) for user, pub_key in self.metadata['sshKeys'].items()]
            ssh_keys = {'sshKeys': Utils.create_file('ssh_keys', '\n'.join(ssh_strings), 'raw')}
            results = self._create_metadata(self.metadata, ssh_keys)

            # remove them and continue
            del self.metadata['sshKeys']

            if len(self.metadata.keys()) == 0:
                return results


        new_results = self._create_metadata(self.metadata, self.metadata_from_file)
        if results:
            return [results, new_results]

        return new_results

# vim: expandtab:tabstop=4:shiftwidth=4

#def parse_metadata(path):
#    '''grab the metadata from file so we can compare it with existing metadata'''
#
#    if not os.path.exists(path):
#        raise GcloudComputeProjectInfoError('Error finding path to metadata file [%s]' % path)
#
#    metadata = {}
#
#    with open(path) as _metafd:
#        for line in _metafd.readlines():
#            if line:
#                key, value = line.split(':')
#            metadata[key] = value
#
#
#    return metadata

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud compute project_info'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            metadata=dict(default=None, type='dict'),
            metadata_from_file=dict(default=None, type='dict'),
            remove_keys=dict(default=None, type='list'),
            remove_all=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['metadata', 'metadata_from_file'],
                            ['remove_keys', 'remove_all'],
                           ]
    )


    #metadata = module.params['metadata']
    #if not metadata and module.params['metadata_from_file']:
    #    # read in metadata and parse it
    #    metadata = {}
    #    for _, val in module.params['metadata_from_file'].items():
    #        metadata.update(parse_metadata(val))

    gcloud = GcloudComputeProjectInfo(module.params['metadata'],
                                      module.params['metadata_from_file'],
                                      module.params.get('remove_keys', None),
                                     )

    state = module.params['state']

    api_rval = gcloud.list_metadata()

    #####
    # Get
    #####
    if state == 'list':
        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="list")

        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if module.params['remove_all'] or gcloud.keys_exist():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = gcloud.delete_metadata(remove_all=module.params['remove_all'])

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not gcloud.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = gcloud.create_metadata()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        # update
        elif gcloud.needs_update():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed an update.')

            api_rval = gcloud.create_metadata()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present|update")

        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudComputeImage('rhel-7-base-2016-06-10')
#    print gcloud.list_images()


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
