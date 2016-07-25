# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class VMInstance(GCPResource):
    '''Object to represent a gcp instance'''

    resource_type = "compute.v1.instance"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 machine_type,
                 metadata,
                 tags,
                 disks,
                 network_interfaces,
                ):
        '''constructor for gcp resource'''
        super(VMInstance, self).__init__(rname, VMInstance.resource_type, project, zone)
        self._machine_type = machine_type
        self._machine_type_url = None
        self._tags = tags
        self._metadata = []
        if metadata and isinstance(metadata, dict):
            self._metadata = {'items': [{'key': key, 'value': value} for key, value in metadata.items()]}
        elif metadata and isinstance(metadata, list):
            self._metadata = [{'key': label['key'], 'value': label['value']} for label in metadata]
        self._disks = disks
        self._network_interfaces = network_interfaces
        self._properties = None

    @property
    def network_interfaces(self):
        '''property for resource machine network_interfaces '''
        return self._network_interfaces

    @property
    def machine_type(self):
        '''property for resource machine type '''
        return self._machine_type

    @property
    def machine_type_url(self):
        '''property for resource machine type url'''
        if self._machine_type_url == None:
            self._machine_type_url = Utils.zonal_compute_url(self.project, self.zone, 'machineTypes', self.machine_type)
        return  self._machine_type_url

    @property
    def tags(self):
        '''property for resource tags '''
        return self._tags

    @property
    def metadata(self):
        '''property for resource metadata'''
        return self._metadata

    @property
    def disks(self):
        '''property for resource disks'''
        return self._disks

    @property
    def properties(self):
        '''property for holding the properties'''
        if self._properties == None:
            self._properties = {'zone': self.zone,
                                'machineType': self.machine_type_url,
                                'metadata': self.metadata,
                                'tags': self.tags,
                                'disks': self.disks,
                                'networkInterfaces': self.network_interfaces,
                               }
        return self._properties

    def to_resource(self):
        '''return the resource representation'''
        return {'name': self.name,
                'type': VMInstance.resource_type,
                'properties': self.properties,
               }
