# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudDeploymentManager(GcloudCLI):
    ''' Class to wrap the gcloud deployment manager '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 dname,
                 config=None,
                 opts=None,
                 credentials=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudDeploymentManager, self).__init__()
        self.dname = dname
        self.opts = opts
        self.config = config
        self.credentials = credentials

    def list_deployments(self):
        '''return deployment'''
        results = self._list_deployments()
        if results['returncode'] == 0:
            results['results'] = results['results'].strip().split('\n')

        return results

    def exists(self):
        ''' return whether a deployment exists '''
        deployments = self.list_deployments()
        if deployments['returncode'] != 0:
            raise GcloudCLIError('Something went wrong.  Results: %s' % deployments['stderr'])
        return self.dname in deployments['results']


    def delete(self):
        '''delete a deployment'''
        return self._delete_deployment(self.dname)

    def create_deployment(self):
        '''create a deployment'''
        return self._create_deployment(self.dname, self.config, self.opts)

    def update_deployment(self):
        '''update a deployment'''
        return self._update_deployment(self.dname, self.config, self.opts)

