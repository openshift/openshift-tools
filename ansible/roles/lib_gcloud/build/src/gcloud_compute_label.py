# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudComputeLabel(GcloudCLI):
    ''' Class to wrap the gcloud compute images command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 project,
                 zone,
                 labels,
                 name=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeLabel, self).__init__(None, project)
        self.zone = zone
        self.labels = labels
        self.verbose = verbose
        self.name = name
        self.existing_labels = {}
        self.existing_metadata = None

    # gcp returns a list of labels as a list of [{ 'key': 'key_value', 'value': 'value_value'
    # this is hard to work with.  this will create one big dict of them
    def gcp_labels_to_dict(self, label_list):
        ''' let's make a dict out of the labels that GCP returns '''

        # Moving the {"key" : "key_value", "value" : "value_value" }
        # to { "key_value" : "value_value"
        for i in label_list:
            self.existing_labels[i['key']] = i['value']

    def get_labels(self):
        ''' get a list of labels '''

        results = self._list_metadata('instances', self.name, self.zone)
        if results['returncode'] == 0:
            self.existing_metadata = yaml.load(results['results'])
            self.gcp_labels_to_dict(self.existing_metadata['metadata']['items'])

            results['instance_metadata'] = self.existing_metadata
            results['instance_labels'] = self.existing_labels
            results.pop('results', None)

            # Set zone if not already set
            if not self.zone:
                self.zone = self.existing_metadata['zone'].split('/')[-1]
                print self.zone

        return results

    def delete_labels(self):
        ''' remove labels from a disk '''

        label_keys_to_be_deleted = []

        for i in self.labels.keys():
            if i in self.existing_labels:
                label_keys_to_be_deleted.append(i)

        if label_keys_to_be_deleted:
            results = self._delete_metadata('instances', label_keys_to_be_deleted, False, self.name, self.zone)
            self.get_labels()
            results['instance_labels'] = self.existing_labels

            return results
        else:
            return {'no_deletes_needed' : True, 'instance_labels' : self.existing_labels}

    def create_labels(self, labels=None):
        '''set the labels for a disk'''

        labels_to_create = {}
        for i in self.labels.keys():
            if i in self.existing_labels:
                if self.labels[i] != self.existing_labels[i]:
                    labels_to_create[i] = self.labels[i]
            else:
                labels_to_create[i] = self.labels[i]

        if labels_to_create:
            results = self._create_metadata('instances', labels_to_create, name=self.name, zone=self.zone)
            self.get_labels()
            results['instance_labels'] = self.existing_labels

            return results
        else:
            return {'no_creates_needed' : True, 'instance_labels' : self.existing_labels}

    # pylint: disable=too-many-return-statements
    @staticmethod
    def run_ansible(params, check_mode):
        ''' run the ansible code '''

        compute_labels = GcloudComputeLabel(params['project'],
                                            params['zone'],
                                            params['labels'],
                                            params['name'],
                                           )

        state = params['state']
        api_rval = compute_labels.get_labels()

        #####
        # Get
        #####
        if state == 'list':
            if api_rval['returncode'] != 0:
                return {'failed': True, 'msg' : api_rval, 'state' : state}

            return {'changed' : False, 'results' : api_rval, 'state' : state}

        ########
        # Delete
        ########
        if state == 'absent':

            api_rval = compute_labels.delete_labels()

            if check_mode:
                return {'changed': False, 'msg': 'Would have performed a delete.'}

            if 'returncode' in api_rval and api_rval['returncode'] != 0:
                return {'failed': True, 'msg': api_rval, 'state': state}

            if "no_deletes_needed" in api_rval:
                return {'changed': False, 'state': "absent", 'results': api_rval}

            return {'changed': True, 'results': api_rval, 'state': state}

        ########
        # Create
        ########
        if state == 'present':

            api_rval = compute_labels.create_labels()

            if check_mode:
                return {'changed': False, 'msg': 'Would have performed a create.'}

            if 'returncode' in api_rval and api_rval['returncode'] != 0:
                return {'failed': True, 'msg': api_rval, 'state': state}

            if "no_creates_needed" in api_rval:
                return {'changed': False, 'state': "present", 'results': api_rval}

            return {'changed': True, 'results': api_rval, 'state': state}

        return {'failed': True, 'changed': False, 'msg': 'Unknown state passed. %s' % state, 'state' : "unknown"}
