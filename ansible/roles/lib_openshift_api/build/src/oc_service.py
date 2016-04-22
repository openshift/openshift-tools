# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCService(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'Service'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 labels,
                 selector,
                 cluster_ip,
                 portal_ip,
                 ports,
                 session_affinity,
                 service_type,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCService, self).__init__(namespace, kubeconfig)
        self.namespace = namespace
        self.config = ServiceConfig(sname, namespace, ports, selector, labels,
                                    cluster_ip, portal_ip, session_affinity, service_type)
        self.user_svc = Service(content=self.config.data)
        self.svc = None

    @property
    def service(self):
        ''' property function service'''
        if not self.svc:
            self.get()
        return self.svc

    @service.setter
    def service(self, data):
        ''' setter function for yedit var '''
        self.svc = data

    def exists(self):
        ''' return whether a volume exists '''
        if self.service:
            return True

        return False

    def get(self):
        '''return volume information '''
        result = self._get(self.kind, self.config.name)
        if result['returncode'] == 0:
            self.service = Service(content=result['results'][0])
            result['clusterip'] = self.service.get('spec#clusterIP')

        return result

    def delete(self):
        '''delete the object'''
        return self._delete(self.kind, self.config.name)

    def create(self):
        '''create a service '''
        return self._create_from_content(self.config.name, self.user_svc.yaml_dict)

    def update(self):
        '''create a service '''
        # Need to copy over the portalIP and the serviceIP settings

        self.user_svc.add_cluster_ip(self.service.get('spec#clusterIP'))
        self.user_svc.add_portal_ip(self.service.get('spec#portalIP'))
        return self._replace_content(self.kind, self.config.name, self.user_svc.yaml_dict)

    def needs_update(self):
        ''' verify an update is needed '''
        skip = ['clusterIP', 'portalIP']
        return not Utils.check_def_equal(self.user_svc.yaml_dict, self.service.yaml_dict, skip_keys=skip, debug=True)


