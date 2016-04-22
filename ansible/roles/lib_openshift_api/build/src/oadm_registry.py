# pylint: skip-file

class RegistryException(Exception):
    ''' Registry Exception Class '''
    pass

class RegistryConfig(OpenShiftCLIConfig):
    ''' RegistryConfig is a DTO for the registry.  '''
    def __init__(self, rname, namespace, kubeconfig, registry_options):
        super(RegistryConfig, self).__init__(rname, namespace, kubeconfig, registry_options)

class Registry(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    volume_mount_path = 'spec#template#spec#containers[0]volumesMounts'
    volume_path = 'spec#template#spec#volumes'
    env_path = 'spec#template#spec#containers[0]#env'

    def __init__(self,
                 registry_config,
                 verbose=False):
        ''' Constructor for OpenshiftOC

           a registry consists of 3 or more parts
           - dc/docker-registry
           - svc/docker-registry
        '''
        super(Registry, self).__init__('default', registry_config.kubeconfig, verbose)
        self.svc_ip = None
        self.config = registry_config
        self.verbose = verbose
        self.registry_parts = [{'kind': 'dc', 'name': self.config.name},
                               {'kind': 'svc', 'name': self.config.name},
                              ]

        self.__registry_prep = None
        self.volume_mounts = []
        self.volumes = []
        if self.config.config_options['volume_mounts']['value']:
            for volume in self.config.config_options['volume_mounts']['value']:
                volume_info = {'secret_name': volume.get('secret_name', None),
                               'name':        volume.get('name', None),
                               'type':        volume.get('type', None),
                               'path':        volume.get('path', None),
                               'claimName':   volume.get('claim_name', None),
                               'claimSize':   volume.get('claim_size', None),
                              }

                vol, vol_mount = Volume.create_volume_structure(volume_info)
                self.volumes.append(vol)
                self.volume_mounts.append(vol_mount)

        self.dconfig = None
        self.svc = None

    @property
    def deploymentconfig(self):
        ''' deploymentconfig property '''
        return self.dconfig

    @deploymentconfig.setter
    def deploymentconfig(self, config):
        ''' setter for deploymentconfig property '''
        self.dconfig = config

    @property
    def service(self):
        ''' service property '''
        return self.svc

    @service.setter
    def service(self, config):
        ''' setter for service property '''
        self.svc = config

    @property
    def registry_prep(self):
        ''' registry_prep property '''
        if not self.__registry_prep:
            results = self.prep_registry()
            if not results:
                raise RegistryException('Could not perform registry preparation.')
            self.__registry_prep = results

        return self.__registry_prep

    @registry_prep.setter
    def registry_prep(self, data):
        ''' setter method for registry_prep attribute '''
        self.__registry_prep = data

    def get(self):
        ''' return the self.registry_parts '''
        self.deploymentconfig = None
        self.service = None

        for part in self.registry_parts:
            result = self._get(part['kind'], rname=part['name'])
            if result['returncode'] == 0 and part['kind'] == 'dc':
                self.deploymentconfig = DeploymentConfig(result['results'][0])
            elif result['returncode'] == 0 and part['kind'] == 'svc':
                self.service = Yedit(content=result['results'][0])

        return (self.deploymentconfig, self.service)

    def exists(self):
        '''does the object exist?'''
        self.get()
        if self.deploymentconfig or self.service:
            return True

        return False

    def delete(self):
        '''return all pods '''
        parts = []
        for part in self.registry_parts:
            parts.append(self._delete(part['kind'], part['name']))

        return parts

    def prep_registry(self):
        ''' prepare a registry for instantiation '''
        options = self.config.to_option_list()

        cmd = ['registry', '-n', self.config.namespace]
        cmd.extend(options)
        cmd.extend(['--dry-run=True', '-o', 'json'])

        results = self.openshift_cmd(cmd, oadm=True, output=True, output_type='json')
        # probably need to parse this
        # pylint thinks results is a string
        # pylint: disable=no-member
        if results['returncode'] != 0 and results['results'].has_key('items'):
            return results

        service = None
        deploymentconfig = None
        # pylint: disable=invalid-sequence-index
        for res in results['results']['items']:
            if res['kind'] == 'DeploymentConfig':
                deploymentconfig = DeploymentConfig(res)
            elif res['kind'] == 'Service':
                service = res

        # Verify we got a service and a deploymentconfig
        if not service or not deploymentconfig:
            return results

        # results will need to get parsed here and modifications added
        deploymentconfig = self.add_modifications(deploymentconfig)

        # modify service ip
        if self.svc_ip:
            service.put('spec#clusterIP', self.svc_ip)

        # need to create the service and the deploymentconfig
        service_file = Utils.create_file('service', service)
        deployment_file = Utils.create_file('deploymentconfig', deploymentconfig)

        return {"service": service, "service_file": service_file,
                "deployment": deploymentconfig, "deployment_file": deployment_file}

    def create(self):
        '''Create a registry'''
        results = []
        for config_file in ['deployment_file', 'service_file']:
            results.append(self._create(self.registry_prep[config_file]))

        # Clean up returned results
        rval = 0
        for result in results:
            if result['returncode'] != 0:
                rval = result['returncode']


        return {'returncode': rval, 'results': results}

    def update(self):
        '''run update for the registry.  This performs a delete and then create '''
        # Store the current service IP
        self.get()
        if self.deploymentconfig:
            svcip = self.deploymentconfig.get('spec#clusterIP')
            if svcip:
                self.svc_ip = svcip

        parts = self.delete()
        for part in parts:
            if part['returncode'] != 0:
                if part.has_key('stderr') and 'not found' in part['stderr']:
                    # the object is not there, continue
                    continue
                # something went wrong
                return parts

        # Ugly built in sleep here.
        #time.sleep(10)

        results = []
        for config_file in ['deployment_file', 'service_file']:
            results.append(self._create(self.registry_prep[config_file]))

        # Clean up returned results
        rval = 0
        for result in results:
            if result['returncode'] != 0:
                rval = result['returncode']

        return {'returncode': rval, 'results': results}

    def add_modifications(self, deploymentconfig):
        ''' update a deployment config with changes '''
        # Currently we know that our deployment of a registry requires a few extra modifications
        # Modification 1
        # we need specific environment variables to be set
        for key, value in self.config.config_options['env_vars']['value'].items():
            if not deploymentconfig.exists_env_value(key, value):
                deploymentconfig.add_env_value(key, value)
            else:
                deploymentconfig.update_env_var(key, value)

        # Modification 2
        # we need specific volume variables to be set
        for volume in self.volumes:
            deploymentconfig.update_volume(volume)

        for vol_mount in self.volume_mounts:
            deploymentconfig.update_volume_mount(vol_mount)

        # Modification 3
        # Edits
        edit_results = []
        for key, value in self.config.config_options['edits']['value'].items():
            edit_results.append(deploymentconfig.put(key, value))

        if not any([res[0] for res in edit_results]):
            return None

        return deploymentconfig.yaml_dict

    def needs_update(self, verbose=False):
        ''' check to see if we need to update '''
        if not self.service or not self.deploymentconfig:
            return True

        exclude_list = ['clusterIP', 'portalIP', 'type', 'protocol']
        if not Utils.check_def_equal(self.registry_prep['service'],
                                     self.service.yaml_dict,
                                     exclude_list,
                                     verbose):
            return True

        exclude_list = ['dnsPolicy',
                        'terminationGracePeriodSeconds',
                        'restartPolicy', 'timeoutSeconds',
                        'livenessProbe', 'readinessProbe',
                        'terminationMessagePath',
                        'rollingParams',
                        'securityContext',
                        'imagePullPolicy',
                        'protocol', #ports.portocol: TCP
                        'type', #strategy: {'type': 'rolling'}
                       ]

        if not Utils.check_def_equal(self.registry_prep['deployment'],
                                     self.deploymentconfig.yaml_dict,
                                     exclude_list,
                                     verbose):
            return True

        return False
