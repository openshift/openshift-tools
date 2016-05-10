# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCScale(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 resource_name,
                 namespace,
                 replicas,
                 kind,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OCScale '''
        super(OCScale, self).__init__(namespace, kubeconfig)
        self.kind = kind
        self.replicas = replicas
        self.name = resource_name
        self.namespace = namespace
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._resource = None

    @property
    def resource(self):
        ''' property function for resource var '''
        if not self._resource:
            self.get()
        return self._resource

    @resource.setter
    def resource(self, data):
        ''' setter function for resource var '''
        self._resource = data

    def get(self):
        '''return replicas information '''
        vol = self._get(self.kind, self.name)
        if vol['returncode'] == 0:
            if self.kind == 'dc':
                self.resource = DeploymentConfig(content=vol['results'][0])
                vol['results'] = [self.resource.get_replicas()]

        return vol

    def put(self):
        '''update replicas into dc '''
        self.resource.update_replicas(self.replicas)
        #self.resource.get_volumes()
        #self.resource.update_volume_mount(self.volume_mount)
        return self._replace_content(self.kind, self.name, self.resource.yaml_dict)

    def needs_update(self):
        ''' verify whether an update is needed '''
        return self.resource.needs_update_replicas(self.replicas)
