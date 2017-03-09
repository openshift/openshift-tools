# pylint: skip-file

class GcloudComputeProjectInfoError(Exception):
    '''exception class for projectinfo'''
    pass

# pylint: disable=too-many-instance-attributes
class GcloudComputeProjectInfo(GcloudCLI):
    ''' Class to wrap the gcloud compute projectinfo command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 metadata=None,
                 metadata_from_file=None,
                 remove_keys=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeProjectInfo, self).__init__()
        self._metadata = metadata
        self.metadata_from_file = metadata_from_file
        self.remove_keys = remove_keys
        self._existing_metadata = None
        self.verbose = verbose

    @property
    def metadata(self):
        '''property for existing metadata'''
        return self._metadata

    @property
    def existing_metadata(self):
        '''property for existing metadata'''
        if self._existing_metadata == None:
            self._existing_metadata = []
            metadata = self.list_metadata()
            metadata = metadata['results']['commonInstanceMetadata']
            if metadata.has_key('items'):
                self._existing_metadata = metadata['items']

        return self._existing_metadata

    def list_metadata(self):
        '''return metatadata'''
        results = self._list_metadata('project-info')
        if results['returncode'] == 0:
            results['results'] = yaml.load(results['results'])

        return results

    def exists(self):
        ''' return whether the metadata that we are removing exists '''
        # currently we aren't opening up files for comparison so always return False
        if self.metadata_from_file:
            return False

        for key, val in self.metadata.items():
            for data in self.existing_metadata:
                if key == 'sshKeys' and data['key'] == key:
                    ssh_keys = {}
                    # get all the users and their public keys out of the project
                    for user_pub_key in data['value'].strip().split('\n'):
                        col_index = user_pub_key.find(':')
                        user = user_pub_key[:col_index]
                        pub_key = user_pub_key[col_index+1:]
                        ssh_keys[user] = pub_key
                    # compare the users that were passed in to see if we need to update
                    for inc_user, inc_pub_key in val.items():
                        if not ssh_keys.has_key(inc_user) or ssh_keys[inc_user] != inc_pub_key:
                            return False
                    # matched all ssh keys
                    break

                elif data['key'] == str(key) and str(data['value']) == str(val):
                    break
            else:
                return False

        return True

    def keys_exist(self):
        ''' return whether the keys exist in the metadata'''
        for key in self.remove_keys:
            for mdata in self.existing_metadata:
                if key == mdata['key']:
                    break

            else:
                # NOT FOUND
                return False

        return True

    def needs_update(self):
        ''' return whether an we need to update '''
        # compare incoming values with metadata returned
        # for each key in user supplied check against returned data
        return not self.exists()

    def delete_metadata(self, remove_all=False):
        ''' attempt to remove metadata '''
        return self._delete_metadata(self.remove_keys, remove_all=remove_all)

    def create_metadata(self):
        '''create an metadata'''
        results = None
        if self.metadata and self.metadata.has_key('sshKeys'):
            # create a file and pass it to create
            ssh_strings = ["%s:%s" % (user, pub_key) for user, pub_key in self.metadata['sshKeys'].items()]
            ssh_keys = {'sshKeys': Utils.create_file('ssh_keys', '\n'.join(ssh_strings), 'raw')}
            results = self._create_metadata('project-info', self.metadata, ssh_keys)

            # remove them and continue
            del self.metadata['sshKeys']

            if len(self.metadata.keys()) == 0:
                return results


        new_results = self._create_metadata('project-info', self.metadata, self.metadata_from_file)
        if results:
            return [results, new_results]

        return new_results

