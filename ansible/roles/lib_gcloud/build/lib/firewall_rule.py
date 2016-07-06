# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class FirewallRule(GCPResource):
    '''Object to represent a gcp forwarding rule'''

    resource_type = "compute.v1.firewall"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 network,
                 allowed,
                 target_tags,
                 source_ranges=None,
                 source_tags=None,
                ):
        '''constructor for gcp resource'''
        super(FirewallRule, self).__init__(rname,
                                           FirewallRule.resource_type,
                                           project,
                                           zone)
        self._desc = desc
        self._allowed = allowed
        self._network = '$(ref.%s.selfLink)' % network
        self._target_tags = target_tags

        self._source_ranges = []
        if source_ranges:
            self._source_ranges = source_ranges

        self._source_tags = []
        if source_tags:
            self._source_tags = source_tags

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def target_tags(self):
        '''property for resource target_tags'''
        return self._target_tags

    @property
    def source_tags(self):
        '''property for resource source_tags'''
        return self._source_tags

    @property
    def source_ranges(self):
        '''property for resource source_ranges'''
        return self._source_ranges

    @property
    def allowed(self):
        '''property for resource allowed'''
        return self._allowed

    @property
    def network(self):
        '''property for resource network'''
        return self._network

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': FirewallRule.resource_type,
                'properties': {'description': self.description,
                               'network': self.network,
                               'sourceRanges': self.source_ranges,
                               'sourceTags': self.source_tags,
                               'allowed': self.allowed,
                               'targetTags': self.target_tags,
                              }
               }

