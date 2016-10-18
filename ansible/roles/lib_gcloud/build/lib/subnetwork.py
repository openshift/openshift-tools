# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class Subnetwork(GCPResource):
    '''Object to represent a gcp subnetwork'''

    resource_type = "compute.v1.subnetwork"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 ip_cidr_range,
                 region,
                 network,
                ):
        '''constructor for gcp resource'''
        super(Subnetwork, self).__init__(rname,
                                         Subnetwork.resource_type,
                                         project,
                                         zone)
        self._ip_cidr_range = ip_cidr_range
        self._region = region
        self._network = '$(ref.%s.selfLink)' % network

    @property
    def ip_cidr_range(self):
        '''property for resource ip_cidr_range'''
        return self._ip_cidr_range

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    @property
    def network(self):
        '''property for resource network'''
        return self._network

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Subnetwork.resource_type,
                'properties': {'ipCidrRange': self.ip_cidr_range,
                               'network': self.network,
                               'region': self.region,
                              }
               }

