# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class TargetPool(GCPResource):
    '''Object to represent a gcp targetPool'''

    resource_type = "compute.v1.targetPool"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 region,
                 health_checks=None, #pd-ssd, local-ssd
                 instances=None,
                 session_affinity=None,
                ):
        '''constructor for gcp resource'''
        super(TargetPool, self).__init__(rname,
                                         TargetPool.resource_type,
                                         project,
                                         zone)
        self._region = region
        self._desc = desc
        self._session_affinity = session_affinity

        self._instances = instances
        self._health_checks = health_checks

        self._instance_refs = None
        self._health_checks_refs = None

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    @property
    def session_affinity(self):
        '''property for resource session_affinity'''
        return self._session_affinity

    @property
    def instances(self):
        '''property for resource instances'''
        return self._instances

    @property
    def health_checks(self):
        '''property for resource health_checks'''
        return self._health_checks

    @property
    def instance_refs(self):
        '''property for resource instance references type'''
        if self._instance_refs == None:
            self._instance_refs = ['$(ref.%s.selfLink)' % inst for inst in self.instances]
        return self._instance_refs

    @property
    def health_checks_refs(self):
        '''property for resource health_checks'''
        if self._health_checks_refs == None:
            self._health_checks_refs = ['$(ref.%s.selfLink)' % check for check in self.health_checks]
        return self._health_checks_refs

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': TargetPool.resource_type,
                'properties': {'description': self.description,
                               'healthChecks': self.health_checks_refs,
                               'instances': self.instance_refs,
                               'sessionAffinity': 'NONE',
                               'region': self.region,
                              }
               }

