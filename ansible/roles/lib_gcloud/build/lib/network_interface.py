# pylint: skip-file

# pylint: disable=too-many-instance-attributes,interface-not-implemented
class NetworkInterface(GCPResource):
    '''Object to represent a gcp disk'''

    #resource_type = "compute.v1."
    resource_type = ''

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 network,
                 subnet,
                 access_config_name=None,
                 access_config_type=None,
                ):
        '''constructor for gcp resource'''
        super(NetworkInterface, self).__init__(rname,
                                               NetworkInterface.resource_type,
                                               project,
                                               zone)
        if not access_config_name and not access_config_type:
            self._access_config = None
        else:
            self._access_config = [{'name': access_config_name or 'default',
                                    'type': access_config_type or 'ONE_TO_ONE_NAT'}]
        self._network_link = '$(ref.%s.selfLink)' % network
        self._subnet_link = '$(ref.%s.selfLink)' % subnet
        self._network = network
        self._subnet = subnet

    @property
    def access_config(self):
        '''property for resource if boot device is persistent'''
        return self._access_config

    @property
    def network(self):
        '''property for resource network'''
        return self._network

    @property
    def subnet(self):
        '''property for resource subnet'''
        return self._subnet

    def get_instance_interface(self):
        '''return in vminstance format'''
        return {'accessConfigs': self.access_config,
                'network': self._network_link,
                'subnetwork': self._subnet_link,
               }

