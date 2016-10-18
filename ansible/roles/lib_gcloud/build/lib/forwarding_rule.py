# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class ForwardingRule(GCPResource):
    '''Object to represent a gcp forwarding rule'''

    resource_type = "compute.v1.forwardingRule"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 ip_address,
                 protocol,
                 region,
                 port_range,
                 target,
                ):
        '''constructor for gcp resource'''
        super(ForwardingRule, self).__init__(rname, ForwardingRule.resource_type, project, zone)
        self._desc = desc
        self._region = region
        self._ip_address = '$(ref.%s.selfLink)' % ip_address
        self._protocol = protocol
        self._port_range = port_range
        self._target = '$(ref.%s.selfLink)' % target

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    @property
    def ip_address(self):
        '''property for resource ip_address'''
        return self._ip_address

    @property
    def protocol(self):
        '''property for resource protocol'''
        return self._protocol

    @property
    def port_range(self):
        '''property for resource port_range'''
        return self._port_range

    @property
    def target(self):
        '''property for resource target'''
        return self._target

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': ForwardingRule.resource_type,
                'properties': {'description': self.description,
                               'region': self.region,
                               'IPAddress': self.ip_address,
                               'IPProtocol': self.protocol,
                               'portRange': self.port_range,
                               'target': self.target,
                              }
               }

