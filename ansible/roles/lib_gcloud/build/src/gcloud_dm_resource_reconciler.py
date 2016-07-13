# pylint: skip-file

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
        resource['properties']['disks'][0]['initializeParams']['diskName'] = \
          resource['properties']['disks'][0]['initializeParams']['diskName'].replace(replace_name, rname)
        docker_name_to_replace = resource['properties']['disks'][1]['source'].split('.')[1]

        resource['properties']['disks'][1]['source'] = \
          resource['properties']['disks'][1]['source'].replace(replace_name, rname)

        # The resources that need to be updated are the following
        # - docker disk names
        # - target pool instance names
        for resource in self.resources:
            # update dockerdisk name
            if docker_name_to_replace == resource['name']:
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

