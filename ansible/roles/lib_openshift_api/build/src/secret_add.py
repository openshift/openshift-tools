# pylint: skip-file

class OCSecretAdd(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    kind = 'sa'
    # pylint allows 5. we need 6
    # pylint: disable=too-many-arguments
    def __init__(self,
                 secrets,
                 service_account,
                 namespace,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(OCSecretAdd, self).__init__(namespace, kubeconfig)
        self.secrets = secrets
        self.service_account = service_account
        self.namespace = namespace
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._yed = None

    @property
    def yed(self):
        ''' Property for the yed var '''
        if not self._yed:
            self.get()
        return self._yed

    @yed.setter
    def yed(self, data):
        ''' setter for the yed var '''
        self._yed = data

    def exists(self, in_secret):
        ''' return whether a key, value  pair exists '''
        secrets = self.yed.get('secrets')
        if not secrets:
            return False

        for secret in secrets:
            if secret['name'] == in_secret:
                return True

        return False

    def get(self):
        '''return a environment variables '''
        env = self._get(OCSecretAdd.kind, self.service_account)
        if env['returncode'] == 0:
            self.yed = Yedit(content=env['results'][0])
            env['results'] = self.yed.get('secrets')
        return env

    def delete(self):
        '''return all pods '''
        service_account = self.get()
        if service_account['returncode'] != 0:
            return service_account

        modified = False
        existing_secrets = self.yed.get('secrets') or []
        for rem_secret in self.secrets:
            for sec_idx, secret in enumerate(existing_secrets):
                idx = None
                if secret['name'] == rem_secret:
                    idx = sec_idx
                    break

            if idx:
                modified = True
                del existing_secrets[idx]

        if modified:
            return self._replace_content(OCSecretAdd.kind, self.service_account, self.yed.yaml_dict)

        return {'returncode': 0, 'changed': False}

    def put(self):
        '''place env vars into dc '''
        modified = False
        existing_secrets = self.yed.get('secrets') or []
        for add_secret in self.secrets:
            if not self.exists(add_secret):
                modified = True
                existing_secrets.append({'name': add_secret})

        if modified:
            return self._replace_content(OCSecretAdd.kind, self.service_account, self.yed.yaml_dict)

        return {'returncode': 0, 'changed': False}

