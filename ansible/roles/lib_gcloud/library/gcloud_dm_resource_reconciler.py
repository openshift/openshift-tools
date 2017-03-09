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


class GcloudResourceReconcilerError(Exception):
    ''' error class for resource reconciler'''
    pass

# pylint: disable=too-many-instance-attributes
class GcloudResourceReconciler(object):
    ''' Class to wrap the gcloud deployment manager '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 resources,
                 instance_counts,
                 existing_instance_info=None,
                 current_dm_config=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        #super(GcloudDeploymentManager, self).__init__()
        self.resources = resources
        self.instance_counts = instance_counts
        self.existing_instance_info = existing_instance_info
        self.current_dm_config = current_dm_config
        self.verbose = verbose

    @staticmethod
    def metadata_todict(item_arr):
        '''convert the array of metadata into a dict'''
        metadata = {}
        for mdata in item_arr:
            metadata[mdata['key']] = mdata['value']

        return metadata

    def gather_instance_resources(self):
        '''compare the resources with the aready existing instances '''

        masters = []
        infra = []
        compute = []
        for resource in self.resources:
            if resource['type'] == 'compute.v1.instance' and \
               resource['properties'].has_key('metadata') and \
               resource['properties']['metadata'].has_key('items'):
                # find the host-type if it exists
                mdata = self.metadata_todict(resource['properties']['metadata']['items'])
                if mdata.has_key('host-type') and mdata['host-type'] == 'master':
                    masters.append(resource)
                    continue
                elif mdata.has_key('host-type') and mdata['host-type'] == 'node' and \
                   mdata.has_key('sub-host-type') and mdata['sub-host-type'] == 'infra':
                    infra.append(resource)
                elif mdata.has_key('host-type') and mdata['host-type'] == 'node' and \
                   mdata.has_key('sub-host-type') and mdata['sub-host-type'] == 'compute':
                    compute.append(resource)

        return {'master': masters, 'infra': infra, 'compute': compute}

    def resource_swap(self, rname, resource):
        '''swap out the name into the resource'''
        # Currently the named objects are the following
        # name:
        replace_name = resource['name']
        resource['name'] = resource['name'].replace(replace_name, rname)
        os_name_to_replace = resource['properties']['disks'][0]['source'].split('.')[1]
        docker_name_to_replace = resource['properties']['disks'][1]['source'].split('.')[1]

        resource['properties']['disks'][1]['source'] = \
          resource['properties']['disks'][1]['source'].replace(replace_name, rname)

        # The resources that need to be updated are the following
        # - docker disk names
        # - target pool instance names
        for resource in self.resources:
            # update dockerdisk name
            if docker_name_to_replace == resource['name'] or os_name_to_replace == resource['name']:
                resource['name'] = resource['name'].replace(replace_name, rname)

            # Update targetpool
            elif '-targetpool' in resource['name']:
                for idx, inst in enumerate(resource['properties']['instances']):
                    if replace_name in inst:
                        resource['properties']['instances'][idx] = \
                          resource['properties']['instances'][idx].replace(replace_name, rname)
                        break


    def reconcile_count(self, new_resources):
        '''check the existing instances against the count'''
        instance_types = ['master', 'infra', 'compute']
        for inst_type in instance_types:
            if not self.existing_instance_info:
                break

            if len(self.existing_instance_info[inst_type]) <= self.instance_counts[inst_type]:
                # Now swap out existing instances with the new resources
                for exist_name in self.existing_instance_info[inst_type]:
                    # Does name exist in new_resources?
                    for res in new_resources[inst_type]:
                        if res['name'] == exist_name:
                            break
                    else:
                        if len(new_resources[inst_type]) > 0:
                            self.resource_swap(exist_name, new_resources[inst_type].pop())
                        else:
                            raise GcloudResourceReconcilerError(\
                                   'Ran out of resources to reconcile from input resource list')
            else:
                raise GcloudResourceReconcilerError(\
                'Requesting a delete.  Suggested resources are greater than the instance counts.')

    def get_resources(self):
        '''return the resources in a dict'''
        return {'resources': self.resources}


    def compare_dm_config_resources(self, config_content):
        ''' compare generated resources with the current deployment manager config '''
        # We are going to ensure all of the resource names are the same
        config_names = set([cont['name'] for cont in config_content])
        resource_names = set([res['name'] for res in self.resources])

        return not config_names == resource_names

# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud deployment-manager deployments '''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            resources=dict(required=True, type='dict'),
            instance_counts=dict(default=None, type='dict'),
            existing_instance_names=dict(default=None, type='dict'),
            current_dm_config=dict(default=None, type='dict'),
            state=dict(default='present', type='str', choices=['present']),
        ),
        required_together=[
            ['existing_instance_names', 'instance_counts', 'resources'],
        ],
        supports_check_mode=True,
    )
    gcloud = GcloudResourceReconciler(module.params['resources']['resources'],
                                      module.params['instance_counts'],
                                      module.params['existing_instance_names'],
                                      module.params['current_dm_config'])

    state = module.params['state']

    orig_resources = copy.deepcopy(module.params['resources'])

    ########
    # generate resources
    ########
    if state == 'present':
        # Deployment manager has run but nothing is in the inventory
        if not module.params['existing_instance_names'] and module.params['current_dm_config']:
            raise GcloudResourceReconcilerError(\
             'Found current deployment manager config but no existing resource names.' + \
             'Please update inventory and rerun.')

        # No existing instance names passed so we cannot reconcile.
        if not module.params['existing_instance_names']:
            module.exit_json(changed=False, results=module.params['resources'], run_dm=True)

        inst_resources = gcloud.gather_instance_resources()

        gcloud.reconcile_count(inst_resources)

        results = gcloud.get_resources()

        if module.params['current_dm_config']:
            run_dm = gcloud.compare_dm_config_resources(module.params['current_dm_config']['resources'])

            if results == orig_resources:
                module.exit_json(changed=False, results=orig_resources, run_dm=run_dm)

            module.exit_json(changed=True, results=results, run_dm=run_dm)

        module.exit_json(changed=True, results=results, run_dm=True)

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudResourceReconciler(resources,
#                                      {'master': 1, 'infra': 2, 'compute': 4},
#                                      existing_instance_info)
#    resources = gcloud.gather_instance_resources()
#    gcloud.reconcile_count(resources)
#    print yaml.dump(gcloud.resources, default_flow_style=False)


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
