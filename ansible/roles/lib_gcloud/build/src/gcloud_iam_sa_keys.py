# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudIAMServiceAccountKeys(GcloudCLI):
    ''' Class to wrap the gcloud compute iam service-accounts command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 acc_name,
                 output_path=None,
                 key_format='p12',
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudIAMServiceAccountKeys, self).__init__()
        self._service_account_name = acc_name
        self._output_path = output_path
        self._key_format = key_format
        self.verbose = verbose

    @property
    def key_format(self):
        '''property for key format '''
        return self._key_format

    @property
    def service_account_name(self):
        '''property for service account name'''
        return self._service_account_name

    @service_account_name.setter
    def service_account_name(self, value):
        '''property setter for service_account_name'''
        self._service_account_name = value

    def list_service_account_keys(self):
        '''return service account key ids'''
        return self._list_service_account_keys(self.service_account_name)

    def delete_service_account_key(self, key_id):
        ''' delete key by id'''
        # compare incoming values with service account returned
        # does the display name exist?
        return self._delete_service_account_key(self.service_account_name, key_id)

    def create_service_account_key(self, outputfile):
        '''create an service account key'''
        results = self._create_service_account_key(self.service_account_name, outputfile)
        if results['returncode'] != 0:
            return results

        # we need to dump the private key out and return it
        from OpenSSL import crypto
        p12 = crypto.load_pkcs12(open(outputfile, 'rb').read(), 'notasecret')
        results['results'] = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey()).strip()

        return results
