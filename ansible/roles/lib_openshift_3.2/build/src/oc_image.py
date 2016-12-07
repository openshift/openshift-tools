# pylint: skip-file

# pylint: disable=too-many-arguments
class OCImage(OpenShiftCLI):
    ''' Class to wrap the oc command line tools
    '''
    def __init__(self,
                 namespace,
                 registry_url,
                 image_name,
                 image_tag,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(OCImage, self).__init__(namespace, kubeconfig)
        self.namespace = namespace
        self.registry_url = registry_url
        self.image_name = image_name
        self.image_tag = image_tag
        self.kubeconfig = kubeconfig
        self.verbose = verbose

    def get(self):
        '''return a image by name '''
        results = self._get('imagestream', self.image_name)
        results['exists'] = False
        if results['returncode'] == 0 and results['results'][0]:
            results['exists'] = True

        if results['returncode'] != 0 and '"%s" not found' % self.image_name in results['stderr']:
            results['returncode'] = 0

        return results

    def create(self, url=None, name=None, tag=None):
        '''Create an image '''

        return self._import_image(url, name, tag)
