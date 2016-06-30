# pylint: skip-file

class Address(GCPResource):
    '''Object to represent a gcp address'''

    resource_type = "compute.v1.address"

    # pylint: disable=too-many-arguments
    def __init__(self, rname, project, zone, desc, region):
        '''constructor for gcp resource'''
        super(Address, self).__init__(rname, Address.resource_type, project, zone)
        self._desc = desc
        self._region = region

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Address.resource_type,
                'properties': {'description': self.description,
                               'region': self.region,
                              }
               }

