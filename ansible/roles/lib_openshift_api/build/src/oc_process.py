# pylint: skip-file

class OCProcess(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    # pylint allows 5. we need 6
    # pylint: disable=too-many-arguments
    def __init__(self,
                 namespace,
                 tname=None,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(OCProcess, self).__init__(namespace, kubeconfig)
        self.namespace = namespace
        self.name = tname
        self.kubeconfig = kubeconfig
        self.verbose = verbose

    def process(self):
        '''process a template'''
        return self._process(self.name)
