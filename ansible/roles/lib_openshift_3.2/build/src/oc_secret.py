# pylint: skip-file

import base64

# pylint: disable=too-many-arguments
class Secret(OpenShiftCLI):
    ''' Class to wrap the oc command line tools
    '''
    def __init__(self,
                 namespace,
                 secret_name=None,
                 decode=False,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(Secret, self).__init__(namespace, kubeconfig)
        self.namespace = namespace
        self.name = secret_name
        self.kubeconfig = kubeconfig
        self.decode = decode
        self.verbose = verbose

    def get(self):
        '''return a secret by name '''
        results = self._get('secrets', self.name)
        results['decoded'] = {}
        results['exists'] = False
        if results['returncode'] == 0 and results['results'][0]:
            results['exists'] = True
            if self.decode:
                if results['results'][0].has_key('data'):
                    for sname, value in results['results'][0]['data'].items():
                        results['decoded'][sname] = base64.decodestring(value)

        if results['returncode'] != 0 and '"%s" not found' % self.name in results['stderr']:
            results['returncode'] = 0

        return results

    def delete(self):
        '''delete a secret by name'''
        return self._delete('secrets', self.name)

    def create(self, files=None, contents=None, content_type=None):
        '''Create a secret '''
        if not files:
            files = Utils.create_files_from_contents(contents, content_type=content_type)

        secrets = ["%s=%s" % (sfile['name'], sfile['path']) for sfile in files]
        cmd = ['-n%s' % self.namespace, 'secrets', 'new', self.name]
        cmd.extend(secrets)

        return self.openshift_cmd(cmd)

    def update(self, files, force=False):
        '''run update secret

           This receives a list of file names and converts it into a secret.
           The secret is then written to disk and passed into the `oc replace` command.
        '''
        secret = self.prep_secret(files)
        if secret['returncode'] != 0:
            return secret

        sfile_path = '/tmp/%s' % self.name
        with open(sfile_path, 'w') as sfd:
            sfd.write(json.dumps(secret['results']))

        atexit.register(Utils.cleanup, [sfile_path])

        return self._replace(sfile_path, force=force)

    def prep_secret(self, files=None, contents=None):
        ''' return what the secret would look like if created
            This is accomplished by passing -ojson.  This will most likely change in the future
        '''
        if not files:
            files = Utils.create_files_from_contents(contents)

        secrets = ["%s=%s" % (sfile['name'], sfile['path']) for sfile in files]
        cmd = ['-ojson', '-n%s' % self.namespace, 'secrets', 'new', self.name]
        cmd.extend(secrets)

        return self.openshift_cmd(cmd, output=True)


