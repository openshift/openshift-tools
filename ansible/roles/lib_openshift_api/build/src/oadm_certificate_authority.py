# pylint: skip-file

import OpenSSL.crypto as crypto

class CertificateAuthorityConfig(OpenShiftCLIConfig):
    ''' CertificateAuthorityConfig is a DTO for the oadm ca command '''
    def __init__(self, cmd, kubeconfig, verbose, ca_options):
        super(CertificateAuthorityConfig, self).__init__('ca', 'default', kubeconfig, ca_options)
        self.cmd = cmd
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._ca = ca_options

class CertificateAuthority(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for oadm ca '''
        super(CertificateAuthority, self).__init__('default', config.kubeconfig, verbose)
        self.config = config
        self.verbose = verbose

    def get(self):
        '''get the current cert file

           If a file exists by the same name in the specified location then the cert exists
        '''
        cert = self.config.config_options['cert']['value']
        if cert and os.path.exists(cert):
            return open(cert).read()

        return None

    def create(self):
        '''Create a deploymentconfig '''
        options = self.config.to_option_list()

        cmd = ['ca']
        cmd.append(self.config.cmd)
        cmd.extend(options)

        return self.openshift_cmd(cmd, oadm=True)

    def exists(self):
        ''' check whether the certificate exists and has the clusterIP '''

        cert_path = self.config.config_options['cert']['value']
        if not os.path.exists(cert_path):
            return False

        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_path).read())
        for var in self.config.config_options['hostnames']['value'].split(','):
            if var in cert.get_subject().CN:
                return True

        return False
