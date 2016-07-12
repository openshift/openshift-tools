# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudIAMServiceAccount(GcloudCLI):
    ''' Class to wrap the gcloud compute iam service-accounts command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname=None,
                 display_name=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudIAMServiceAccount, self).__init__()
        self._name = sname
        self._display_name = display_name
        self._exist_sa = None
        self.verbose = verbose

    @property
    def existing_service_accounts(self):
        '''property for existing service ccounts'''
        if self._exist_sa == None:
            self._exist_sa = self._list_service_accounts()['results']
        return self._exist_sa

    @property
    def name(self):
        '''property for name'''
        return self._name

    @name.setter
    def name(self, value):
        '''property setter for name'''
        self._name = value

    @property
    def display_name(self):
        '''property for display_name'''
        return self._display_name

    def list_service_accounts(self):
        '''return metatadata'''
        results = self._list_service_accounts()
        if results['returncode'] != 0:
            if 'Permission denied: service account' in results['stderr']:
                results['results'] = []
        elif results['returncode'] == 0:
            for sacc in results['results']:
                if self.name == sacc['email'] or self.name == sacc['email'].split('@')[0]:
                    results['results'] = sacc
                    break

        return results

    def exists(self):
        ''' return whether the service account exists '''
        for sacc in self.existing_service_accounts:
            if self.name == sacc['email'] or self.name == sacc['email'].split('@')[0]:
                self.name = sacc['email']
                return True

        return False

    def needs_update(self):
        ''' return whether an we need to update '''
        # compare incoming values with service account returned
        # does the display name exist?
        for sacc in self.existing_service_accounts:
            if self.name in sacc['email'] and self.display_name == sacc['displayName']:
                return False

        return True

    def delete_service_account(self):
        ''' attempt to remove service_name '''
        return self._delete_service_account(self.name)

    def create_service_account(self):
        '''create an service_name'''
        return self._create_service_account(self.name, self.display_name)

    def update_service_account(self):
        '''create an service_name'''
        return self._update_service_account(self.name, self.display_name)
