# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class HealthCheck(GCPResource):
    '''Object to represent a gcp health check'''

    resource_type = "compute.v1.httpHealthCheck"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 interval_secs,
                 healthy_threshold,
                 port,
                 timeout_secs,
                 unhealthy_threshold,
                ):
        '''constructor for gcp resource'''
        super(HealthCheck, self).__init__(rname, HealthCheck.resource_type, project, zone)
        self._desc = desc
        self._interval_secs = interval_secs
        self._healthy_threshold = healthy_threshold
        self._unhealthy_threshold = unhealthy_threshold
        self._port = port
        self._timeout_secs = timeout_secs

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def interval_secs(self):
        '''property for resource interval_secs'''
        return self._interval_secs

    @property
    def timeout_secs(self):
        '''property for resource timeout_secs'''
        return self._timeout_secs

    @property
    def healthy_threshold(self):
        '''property for resource healthy_threshold'''
        return self._healthy_threshold

    @property
    def unhealthy_threshold(self):
        '''property for resource unhealthy_threshold'''
        return self._unhealthy_threshold

    @property
    def port(self):
        '''property for resource port'''
        return self._port

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': HealthCheck.resource_type,
                'properties': {'description': self.description,
                               'checkIntervalSec': self.interval_secs,
                               'port': self.port,
                               'healthyThreshold': self.healthy_threshold,
                               'unhealthyThreshold': self.unhealthy_threshold,
                               'timeoutSec': 5,
                              }
               }

