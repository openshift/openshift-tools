# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCLabel(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 name,
                 namespace,
                 kind,
                 kubeconfig,
                 labels=None,
                 selector=None,
                 verbose=False):
        ''' Constructor for OCLabel '''
        super(OCLabel, self).__init__(namespace, kubeconfig)
        self.name = name
        self.namespace = namespace
        self.kind = kind
        self.kubeconfig = kubeconfig
        self.labels = labels
        self.selector = selector

# new
    def get_current_labels(self):
        ''' get the current labels on object '''

        return self.get()['results']['labels']

    def compare_labels(self, host_labels):
        ''' compare labels '''

        for label in self.labels:
            if label['key'] not in host_labels or \
               label['value'] != host_labels[label['key']]:
                return False
        return True

    def all_user_labels_exist(self):
        ''' return whether all the labels already exist '''

        current_labels = self.get_current_labels()

        for current_host_labels in current_labels:
            rbool = self.compare_labels(current_host_labels)
            if rbool == False:
                return False
        return True

    def any_label_exists(self):
        ''' return whether any single label already exists '''
        current_labels = self.get_current_labels()

        for current_host_labels in current_labels:
            for label in self.labels:
                if label['key'] in current_host_labels:
                    return True
        return False

    def get_user_keys(self):
        ''' go through list of user key:values and return all keys '''

        user_keys = []
        for label in self.labels:
            user_keys.append(label['key'])

        return user_keys

    def get_current_label_keys(self):
        ''' collect all the current label keys '''

        current_label_keys = []
        current_labels = self.get_current_labels()
        for current_host_labels in current_labels:
            current_label_keys.appens(current_host_labels.keys())

        return list(set(current_label_keys))

    def get_extra_current_labels(self):
        ''' return list of labels that are currently stored, but aren't
            in user-provided list '''

        current_labels = self.get_current_labels()
        extra_labels = []
        user_label_keys = self.get_user_keys()
        current_label_keys = self.get_current_label_keys()

        for current_key in current_label_keys:
            if current_key not in user_label_keys:
                extra_labels.append(current_key)

        return extra_labels

    def extra_current_labels(self):
        ''' return whether there are labels currently stored that user
            hasn't directly provided '''
        extra_labels = self.get_extra_current_labels()

        if len(extra_labels) > 0:
                return True
        else:
            return False

    def replace(self):
        ''' replace currently stored labels with user provided labels '''
        cmd = self.cmd_template()

        # First delete any extra labels
        extra_labels = self.get_extra_current_labels()
        if len(extra_labels) > 0:
            for label in extra_labels:
                cmd.append("{}-".format(label))

        # Now add/modify the user-provided label list
        if len(self.labels) > 0:
            for label in self.labels:
                cmd.append("{}={}".format(label['key'], label['value']))

        # --overwrite for the case where we are updating existing labels
        cmd.append("--overwrite")
        return self.openshift_cmd(cmd)

    def get(self):
        '''return label information '''

        result_dict = {}
        label_list = []

        if self.name:
            result = self._get(resource=self.kind, rname=self.name, selector=self.selector)

            if 'labels' in result['results'][0]['metadata']:
                label_list.append(result['results'][0]['metadata']['labels'])
            else:
                label_list.append({})

        else:
            result = self._get(resource=self.kind, selector=self.selector)

            for item in result['results'][0]['items']:
                if 'labels' in item['metadata']:
                    label_list.append(item['metadata']['labels'])
                else:
                    label_list.append({})

        result_dict['labels'] = label_list
        result_dict['item_count'] = len(label_list)
        result['results'] = result_dict

        return result

    def cmd_template(self):
        ''' boilerplate oc command for modifying lables on this object '''
        # let's build the cmd with what we have passed in
        cmd = []
        if self.namespace:
            cmd = cmd + ["-n", self.namespace]

        if self.selector:
            cmd = cmd + ["--selector", self.selector]

        cmd = cmd + ["--config", self.kubeconfig, "label", self.kind]

        if self.name:
            cmd = cmd + [self.name]

        return cmd

    def add(self):
        ''' add labels '''
        cmd = self.cmd_template()

        for label in self.labels:
            cmd.append("{}={}".format(label['key'], label['value']))

        cmd.append("--overwrite")

        return self.openshift_cmd(cmd)

    def delete(self):
        '''delete the labels'''
        cmd = self.cmd_template()
        for label in self.labels:
            cmd.append("{}-".format(label['key']))

        return self.openshift_cmd(cmd)
