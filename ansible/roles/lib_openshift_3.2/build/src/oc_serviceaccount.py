# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCServiceAccount(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'sa'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCServiceAccount, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self.namespace = config.namespace
        self._service_account = None

    @property
    def service_account(self):
        ''' property function service'''
        if not self._service_account:
            self.get()
        return self._service_account

    @service_account.setter
    def service_account(self, data):
        ''' setter function for yedit var '''
        self._service_account = data

    def exists(self):
        ''' return whether a volume exists '''
        if self.service_account:
            return True

        return False

    def get(self):
        '''return volume information '''
        result = self._get(self.kind, self.config.name)
        if result['returncode'] == 0:
            self.service_account = ServiceAccount(content=result['results'][0])
        elif '\"%s\" not found' % self.config.name in result['stderr']:
            result['returncode'] = 0
            result['results'] = [{}]

        return result

    def delete(self):
        '''delete the object'''
        return self._delete(self.kind, self.config.name)

    def create(self):
        '''create the object'''
        return self._create_from_content(self.config.name, self.config.data)

    def update(self):
        '''update the object'''
        # need to update the tls information and the service name
        for secret in self.config.secrets:
            result = self.service_account.find_secret(secret)
            if not result:
                self.service_account.add_secret(secret)

        for secret in self.config.image_pull_secrets:
            result = self.service_account.find_image_pull_secret(secret)
            if not result:
                self.service_account.add_image_pull_secret(secret)

        return self._replace_content(self.kind, self.config.name, self.config.data)

    def needs_update(self):
        ''' verify an update is needed '''
        # since creating an service account generates secrets and imagepullsecrets
        # check_def_equal will not work
        # Instead, verify all secrets passed are in the list
        for secret in self.config.secrets:
            result = self.service_account.find_secret(secret)
            if not result:
                return True

        for secret in self.config.image_pull_secrets:
            result = self.service_account.find_image_pull_secret(secret)
            if not result:
                return True

        return False
