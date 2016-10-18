# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCVersion(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 debug):
        ''' Constructor for OCVersion '''
        super(OCVersion, self).__init__(None, config)
        self.debug = debug


    @staticmethod
    def openshift_installed():
        ''' check if openshift is installed '''
        import yum

        yum_base = yum.YumBase()
        if yum_base.rpmdb.searchNevra(name='atomic-openshift'):
            return True
        else:
            return False

    @staticmethod
    def filter_versions(stdout):
        ''' filter the oc version output '''

        version_dict = {}
        version_search = ['oc', 'openshift', 'kubernetes']

        for line in stdout.strip().split('\n'):
            for term in version_search:
                if not line:
                    continue
                if line.startswith(term):
                    version_dict[term] = line.split()[-1]

        # horrible hack to get openshift version in Openshift 3.2
        #  By default "oc version in 3.2 does not return an "openshift" version
        if "openshift" not in version_dict:
            version_dict["openshift"] = version_dict["oc"]

        return version_dict


    @staticmethod
    def add_custom_versions(versions):
        ''' create custom versions strings '''

        versions_dict = {}

        for tech, version in versions.items():
            # clean up "-" from version
            if "-" in version:
                version = version.split("-")[0]

            if version.startswith('v'):
                versions_dict[tech+'_numeric'] = version[1:]
                # "v3.3.0.33" is what we have, we want "3.3"
                versions_dict[tech+'_short'] = version[1:4]

        return versions_dict

    def get(self):
        '''get and return version information '''

        results = {}
        results["installed"] = OCVersion.openshift_installed()

        if not results["installed"]:
            return results

        version_results = self.openshift_cmd(['version'], output=True, output_type='raw')

        if version_results['returncode'] == 0:
            filtered_vers = OCVersion.filter_versions(version_results['results'])
            custom_vers = OCVersion.add_custom_versions(filtered_vers)

            results['returncode'] = version_results['returncode']
            results.update(filtered_vers)
            results.update(custom_vers)

            return results

        raise OpenShiftCLIError('Problem detecting openshift version.')
