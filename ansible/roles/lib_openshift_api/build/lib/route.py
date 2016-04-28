# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class RouteConfig(object):
    ''' Handle route options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 kubeconfig,
                 cacert=None,
                 cert=None,
                 cert_key=None,
                 host=None,
                 tls_termination=None,
                 service_name=None):
        ''' constructor for handling route options '''
        self.kubeconfig = kubeconfig
        self.name = sname
        self.namespace = namespace
        self.host = host
        self.tls_termination = tls_termination
        self.cacert = cacert
        self.cert = cert
        self.cert_key = cert_key
        self.service_name = service_name
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a service as a dict '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = 'Route'
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        self.data['metadata']['namespace'] = self.namespace
        self.data['spec'] = {}

        self.data['spec']['host'] = self.host

        if self.tls_termination:
            self.data['spec']['tls'] = {}

            self.data['spec']['tls']['key'] = self.cert_key
            self.data['spec']['tls']['caCertificate'] = self.cacert
            self.data['spec']['tls']['certificate'] = self.cert
            self.data['spec']['tls']['termination'] = self.tls_termination

        self.data['spec']['to'] = {'kind': 'Service', 'name': self.service_name}

# pylint: disable=too-many-instance-attributes
class Route(Yedit):
    ''' Class to wrap the oc command line tools '''
    service_path = "spec#to#name"
    cert_path = "spec#tls#certificate"
    cacert_path = "spec#tls#caCertificate"
    termination_path = "spec#tls#termination"
    key_path = "spec#tls#key"
    kind = 'route'

    def __init__(self, content):
        '''Route constructor'''
        super(Route, self).__init__(content=content)

    def get_cert(self):
        ''' return cert '''
        return self.get(Route.cert_path)

    def get_cert_key(self):
        ''' return cert key '''
        return self.get(Route.key_path)

    def get_cacert(self):
        ''' return cacert '''
        return self.get(Route.cacert_path)

    def get_service(self):
        ''' return service name '''
        return self.get(Route.service_path)

    def get_termination(self):
        ''' return tls termination'''
        return self.get(Route.termination_path)
