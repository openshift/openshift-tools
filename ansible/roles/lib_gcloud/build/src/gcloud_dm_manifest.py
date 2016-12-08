# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudDeploymentManagerManifests(GcloudCLI):
    ''' Class to wrap the gcloud deployment manager '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 deployment,
                 mname=None,
                 verbose=False):
        ''' Constructor for GcloudDeploymentManagerManifests '''
        super(GcloudDeploymentManagerManifests, self).__init__(verbose=True)
        self.deployment = deployment
        self.name = mname
        self.verbose = verbose

    def list_manifests(self):
        '''return manifest'''
        results = self._list_manifests(self.deployment, self.name)
        #if results['returncode'] == 0:
            #results['results'] = yaml.load(results['results'])

        return results

