# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCVolume(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    volume_mounts_path = {"pod": "spec#containers[0]#volumeMounts",
                          "dc":  "spec#template#spec#containers[0]#volumeMounts",
                          "rc":  "spec#template#spec#containers[0]#volumeMounts",
                         }
    volumes_path = {"pod": "spec#volumes",
                    "dc":  "spec#template#spec#volumes",
                    "rc":  "spec#template#spec#volumes",
                   }

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 kind,
                 resource_name,
                 namespace,
                 vol_name,
                 mount_path,
                 mount_type,
                 secret_name,
                 claim_size,
                 claim_name,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCVolume, self).__init__(namespace, kubeconfig)
        self.kind = kind
        self.volume_info = {'name': vol_name,
                            'secret_name': secret_name,
                            'path': mount_path,
                            'type': mount_type,
                            'claimSize': claim_size,
                            'claimName': claim_name}
        self.volume, self.volume_mount = Volume.create_volume_structure(self.volume_info)
        self.name = resource_name
        self.namespace = namespace
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._resource = None

    @property
    def resource(self):
        ''' property function for resource var '''
        if not self._resource:
            self.get()
        return self._resource

    @resource.setter
    def resource(self, data):
        ''' setter function for resource var '''
        self._resource = data

    def exists(self):
        ''' return whether a volume exists '''
        volume_mount_found = False
        volume_found = self.resource.exists_volume(self.volume)
        if not self.volume_mount and volume_found:
            return True

        if self.volume_mount:
            volume_mount_found = self.resource.exists_volume_mount(self.volume_mount)

        if volume_found and self.volume_mount and volume_mount_found:
            return True

        return False

    def get(self):
        '''return volume information '''
        vol = self._get(self.kind, self.name)
        if vol['returncode'] == 0:
            if self.kind == 'dc':
                self.resource = DeploymentConfig(content=vol['results'][0])
                vol['results'] = self.resource.get_volumes()

        return vol

    def delete(self):
        '''return all pods '''
        self.resource.delete_volume_by_name(self.volume)
        return self._replace_content(self.kind, self.name, self.resource.yaml_dict)

    def put(self):
        '''place env vars into dc '''
        self.resource.update_volume(self.volume)
        self.resource.get_volumes()
        self.resource.update_volume_mount(self.volume_mount)
        return self._replace_content(self.kind, self.name, self.resource.yaml_dict)

    def needs_update(self):
        ''' verify an update is needed '''
        return self.resource.needs_update_volume(self.volume, self.volume_mount)
