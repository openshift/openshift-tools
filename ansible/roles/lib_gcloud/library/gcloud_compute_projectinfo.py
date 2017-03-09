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

import atexit
import json
import os
import random
# Not all genearated modules use this.
# pylint: disable=unused-import
import re
import shutil
import string
import subprocess
import tempfile
import yaml
# Not all genearated modules use this.
# pylint: disable=unused-import
import copy
# pylint: disable=import-error
from apiclient.discovery import build
# pylint: disable=import-error
from oauth2client.client import GoogleCredentials
from ansible.module_utils.basic import AnsibleModule


class GcloudCLIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class GcloudCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self, credentials=None, project=None, verbose=False):
        ''' Constructor for GcloudCLI '''
        self.scope = None
        self._project = project

        if not credentials:
            self.credentials = GoogleCredentials.get_application_default()
        else:
            tmp = tempfile.NamedTemporaryFile()
            tmp.write(json.dumps(credentials))
            tmp.seek(0)
            self.credentials = GoogleCredentials.from_stream(tmp.name)
            tmp.close()

        self.scope = build('compute', 'beta', credentials=self.credentials)

        self.verbose = verbose

    @property
    def project(self):
        '''property for project'''
        return self._project

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

        cmd.append('-q')

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

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _delete_address(self, aname):
        ''' list addresses
            if a name is specified then perform a describe
        '''
        cmd = ['compute', 'addresses', 'delete', aname, '-q']

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

    def _list_metadata(self, resource_type, name=None, zone=None):
        ''' list metadata'''
        cmd = ['compute', resource_type, 'describe']

        if name:
            cmd.extend([name])

        if zone:
            cmd.extend(['--zone', zone])

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    # pylint: disable=too-many-arguments
    def _delete_metadata(self, resource_type, keys, remove_all=False, name=None, zone=None):
        '''create metadata'''
        cmd = ['compute', resource_type, 'remove-metadata']

        if name:
            cmd.extend([name])

        if zone:
            cmd.extend(['--zone', zone])

        if remove_all:
            cmd.append('--all')

        else:
            cmd.append('--keys')
            cmd.append(','.join(keys))

        cmd.append('-q')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    # pylint: disable=too-many-arguments
    def _create_metadata(self, resource_type, metadata=None, metadata_from_file=None, name=None, zone=None):
        '''create metadata'''
        cmd = ['compute', resource_type, 'add-metadata']

        if name:
            cmd.extend([name])

        if zone:
            cmd.extend(['--zone', zone])

        data = None

        if metadata_from_file:
            cmd.append('--metadata-from-file')
            data = metadata_from_file
        else:
            cmd.append('--metadata')
            data = metadata

        cmd.append(','.join(['%s=%s' % (key, val) for key, val in data.items()]))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_service_accounts(self, sa_name=None):
        '''return service accounts '''
        cmd = ['iam', 'service-accounts']
        if sa_name:
            cmd.extend(['describe', sa_name])
        else:
            cmd.append('list')

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _delete_service_account(self, sa_name):
        '''delete service account '''
        cmd = ['iam', 'service-accounts', 'delete', sa_name, '-q']

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _create_service_account(self, sa_name, display_name=None):
        '''create service account '''
        cmd = ['iam', 'service-accounts', 'create', sa_name]
        if display_name:
            cmd.extend(['--display-name', display_name])

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _update_service_account(self, sa_name, display_name=None):
        '''update service account '''
        cmd = ['iam', 'service-accounts', 'update', sa_name]
        if display_name:
            cmd.extend(['--display-name', display_name])

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _delete_service_account_key(self, sa_name, key_id):
        '''delete service account key'''
        cmd = ['iam', 'service-accounts', 'keys', 'delete', key_id, '--iam-account', sa_name, '-q']

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_service_account_keys(self, sa_name):
        '''return service account keys '''
        cmd = ['iam', 'service-accounts', 'keys', 'list', '--iam-account', sa_name]

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _create_service_account_key(self, sa_name, outputfile, key_format='p12'):
        '''create service account key '''
        # Ensure we remove the key file
        atexit.register(Utils.cleanup, [outputfile])

        cmd = ['iam', 'service-accounts', 'keys', 'create', outputfile,
               '--iam-account', sa_name, '--key-file-type', key_format]

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_project_policy(self, project):
        '''create service account key '''
        cmd = ['projects', 'get-iam-policy', project]

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _add_project_policy(self, project, member, role):
        '''create service account key '''
        cmd = ['projects', 'add-iam-policy-binding', project, '--member', member, '--role', role]

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _remove_project_policy(self, project, member, role):
        '''create service account key '''
        cmd = ['projects', 'remove-iam-policy-binding', project, '--member', member, '--role', role]

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _set_project_policy(self, project, policy_path):
        '''create service account key '''
        cmd = ['projects', 'set-iam-policy', project, policy_path]

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _list_zones(self):
        ''' list zones '''
        cmd = ['compute', 'zones', 'list']

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _config_set(self, config_param, config_value, config_section):
        ''' set config params with gcloud config set '''
        param = config_section + '/' + config_param
        cmd = ['config', 'set', param, config_value]

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def _list_config(self):
        '''return config '''
        cmd = ['config', 'list']

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    def list_disks(self, zone=None, disk_name=None):
        '''return a list of disk objects in this project and zone'''
        cmd = ['beta', 'compute', 'disks']
        if disk_name and zone:
            cmd.extend(['describe', disk_name, '--zone', zone])
        else:
            cmd.append('list')

        cmd.extend(['--format', 'json'])

        return self.gcloud_cmd(cmd, output=True, output_type='json')

    # disabling too-many-arguments as these are all required for the disk labels
    # pylint: disable=too-many-arguments
    def _set_disk_labels(self, project, zone, dname, labels, finger_print):
        '''create service account key '''
        if labels == None:
            labels = {}

        self.scope = build('compute', 'beta', credentials=self.credentials)
        body = {'labels': labels, 'labelFingerprint': finger_print}
        result = self.scope.disks().setLabels(project=project,
                                              zone=zone,
                                              resource=dname,
                                              body=body,
                                             ).execute()

        return result

    def gcloud_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for gcloud '''
        cmds = ['/usr/bin/gcloud']

        if self.project:
            cmds.extend(['--project', self.project])

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

        stdout, stderr = proc.communicate()
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
        results = self._list_metadata('project-info')
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
            results = self._create_metadata('project-info', self.metadata, ssh_keys)

            # remove them and continue
            del self.metadata['sshKeys']

            if len(self.metadata.keys()) == 0:
                return results


        new_results = self._create_metadata('project-info', self.metadata, self.metadata_from_file)
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
