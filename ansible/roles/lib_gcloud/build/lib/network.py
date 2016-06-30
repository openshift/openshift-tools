# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class Network(GCPResource):
    '''Object to represent a gcp Network'''

    resource_type = "compute.v1.network"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 auto_create_subnets,
                ):
        '''constructor for gcp resource'''
        super(Network, self).__init__(rname,
                                      Network.resource_type,
                                      project,
                                      zone)
        self._desc = desc
        self._auto_create_subnets = auto_create_subnets

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def auto_create_subnets(self):
        '''property for resource auto_create_subnets'''
        return self._auto_create_subnets

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Network.resource_type,
                'properties': {'description': self.description,
                               'autoCreateSubnetworks': self.auto_create_subnets,
                              }
               }

