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
        self.name = resource_name
        self.vol_name = vol_name
        self.mount_path = mount_path
        self.mount_type = mount_type
        self.namespace = namespace
        self.secret_name = secret_name
        self.claim_name = claim_name
        self.claim_size = claim_size
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._yed = None

    @property
    def yed(self):
        ''' property function for yedit var '''
        if not self._yed:
            self.get()
        return self._yed

    @yed.setter
    def yed(self, data):
        ''' setter function for yedit var '''
        self._yed = data

    def exists(self):
        ''' return whether a volume exists '''
        volumes = self.yed.get(OCVolume.volume_mounts_path[self.kind]) or []
        volume_mounts = self.yed.get(OCVolume.volumes_path[self.kind]) or []

        if not volumes or not volume_mounts:
            return False

        volume_found = False
        for volume in volumes:
            if volume['name'] == self.vol_name:
                volume_found = True
                break

        volume_mount_found = False
        for volume_mount in volume_mounts:
            if volume_mount['name'] == self.vol_name:
                volume_mount_found = True
                break

        if volume_mount_found and volume_found:
            return True

        return False

    def find_volume(self, mounts=False):
        ''' return the index of a volume '''
        volumes = []
        if mounts:
            volumes = self.yed.get(OCVolume.volume_mounts_path[self.kind]) or []
        else:
            volumes = self.yed.get(OCVolume.volumes_path[self.kind]) or []
        for volume in volumes:
            if volume['name'] == self.vol_name:
                return volume

        return None

    def get(self):
        '''return volume information '''
        vol = self._get(self.kind, self.name)
        if vol['returncode'] == 0:
            self.yed = Yedit(content=vol['results'][0])
            vol['results'] = self.yed.get(OCVolume.volumes_path[self.kind]) or []

        return vol

    def delete(self):
        '''return all pods '''
        cmd = ['volume', self.kind, self.name, '--remove', '--name=%s' % self.vol_name, '-n', self.namespace]
        return self.openshift_cmd(cmd)

    def put(self, overwrite=False):
        '''place env vars into dc '''
        cmd = ['volume',
               self.kind,
               self.name,
               '-n', self.namespace,
               '--add',
               '-t', self.mount_type,
               '--name=%s' % self.vol_name,
              ]
        if self.mount_type == 'secret':
            cmd.extend(['-m', self.mount_path,
                        '--secret-name=%s' % self.secret_name,
                       ])
        elif self.mount_type == 'emptydir':
            cmd.extend(['-m', self.mount_path])
        elif self.mount_type == 'pvc':
            cmd.extend(['-m', self.mount_path,
                        '--claim-size=%s' % self.claim_size,
                        '--claim-name=%s' % self.claim_name,
                       ])
        elif self.mount_type == 'hostpath':
            cmd.extend(['--path', self.mount_path])

        if overwrite:
            cmd.append('--overwrite')

        return self.openshift_cmd(cmd)

    def needs_update(self):
        ''' verify an update is needed '''
        volume = self.find_volume()
        volume_mount = self.find_volume(mounts=True)
        results = []
        results.append(volume['name'] == self.vol_name)

        if self.mount_type == 'secret':
            results.append(volume.has_key('secret'))
            results.append(volume['secret']['secretName'] == self.secret_name)
            results.append(volume_mount['name'] == self.vol_name)
            results.append(volume_mount['mountPath'] == self.mount_path)

        elif self.mount_type == 'emptydir':
            results.append(volume_mount['name'] == self.vol_name)
            results.append(volume_mount['mountPath'] == self.mount_path)

        elif self.mount_type == 'pvc':
            results.append(volume.has_key('persistentVolumeClaim'))
            results.append(volume['persistentVolumeClaim']['claimName'] == self.claim_name)

            if volume['persistentVolumeClaim'].has_key('claimSize'):
                results.append(volume['persistentVolumeClaim']['claimSize'] == self.claim_size)

        elif self.mount_type == 'hostpath':
            results.append(volume.has_key('hostPath'))
            results.append(volume['hostPath']['path'] == self.mount_path)

        return not all(results)
