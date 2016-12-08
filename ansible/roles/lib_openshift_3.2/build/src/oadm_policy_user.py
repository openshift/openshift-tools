# pylint: skip-file

class OadmPolicyException(Exception):
    ''' Registry Exception Class '''
    pass

class OadmPolicyUserConfig(OpenShiftCLIConfig):
    ''' RegistryConfig is a DTO for the registry.  '''
    def __init__(self, namespace, kubeconfig, policy_options):
        super(OadmPolicyUserConfig, self).__init__(policy_options['name']['value'],
                                                   namespace, kubeconfig, policy_options)
        self.kind = self.get_kind()
        self.namespace = namespace

    def get_kind(self):
        ''' return the kind we are working with '''
        if self.config_options['resource_kind']['value'] == 'role':
            return 'rolebinding'
        elif self.config_options['resource_kind']['value'] == 'cluster-role':
            return 'clusterrolebinding'
        elif self.config_options['resource_kind']['value'] == 'scc':
            return 'scc'

        return None

class OadmPolicyUser(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    def __init__(self,
                 policy_config,
                 verbose=False):
        ''' Constructor for OadmPolicyUser '''
        super(OadmPolicyUser, self).__init__(policy_config.namespace, policy_config.kubeconfig, verbose)
        self.config = policy_config
        self.verbose = verbose
        self._rolebinding = None
        self._scc = None

    @property
    def role_binding(self):
        ''' role_binding property '''
        return self._rolebinding

    @role_binding.setter
    def role_binding(self, binding):
        ''' setter for role_binding property '''
        self._rolebinding = binding

    @property
    def security_context_constraint(self):
        ''' security_context_constraint property '''
        return self._scc

    @security_context_constraint.setter
    def security_context_constraint(self, scc):
        ''' setter for security_context_constraint property '''
        self._scc = scc

    def get(self):
        '''fetch the desired kind'''
        resource_name = self.config.config_options['name']['value']
        if resource_name == 'cluster-reader':
            resource_name += 's'

        return self._get(self.config.kind, resource_name)

    def exists_role_binding(self):
        ''' return whether role_binding exists '''
        results = self.get()
        if results['returncode'] == 0:
            self.role_binding = RoleBinding(results['results'][0])
            if self.role_binding.find_user_name(self.config.config_options['user']['value']) != None:
                return True

            return False

        elif '\"%s\" not found' % self.config.config_options['name']['value'] in results['stderr']:
            return False

        return results

    def exists_scc(self):
        ''' return whether scc exists '''
        results = self.get()
        if results['returncode'] == 0:
            self.security_context_constraint = SecurityContextConstraints(results['results'][0])

            if self.security_context_constraint.find_user(self.config.config_options['user']['value']):
                return True

            return False

        return results

    def exists(self):
        '''does the object exist?'''
        if self.config.config_options['resource_kind']['value'] == 'cluster-role':
            return self.exists_role_binding()

        elif self.config.config_options['resource_kind']['value'] == 'role':
            return self.exists_role_binding()

        elif self.config.config_options['resource_kind']['value'] == 'scc':
            return self.exists_scc()

        return False

    def perform(self):
        '''perform action on resource'''
        cmd = ['-n', self.config.namespace, 'policy',
               self.config.config_options['action']['value'],
               self.config.config_options['name']['value'],
               self.config.config_options['user']['value']]

        return self.openshift_cmd(cmd, oadm=True)
