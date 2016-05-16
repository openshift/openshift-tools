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
                 verbose=False):
        ''' Constructor for OCLabel '''
        super(OCLabel, self).__init__(namespace, kubeconfig)
        self.name = name
        self.namespace = namespace
        self.kind = kind
        self.kubeconfig = kubeconfig
        self.labels = labels

    def all_user_labels_exist(self):
        ''' return whether all the labels already exist '''
        current_labels = self.get()['results'][0]

        for label in self.labels:
            if label['key'] not in current_labels or \
               label['value'] != current_labels[label['key']]:
                return False

        return True

    def get_user_keys(self):
        ''' go through list of user key:values and return all keys '''
        user_keys = []
        for label in self.labels:
            user_keys.append(label['key'])
        return user_keys

    def get_extra_current_labels(self):
        ''' return list of labels that are currently stored, but aren't
            int user-provided list '''
        extra_labels = []
        current_labels = self.get()['results'][0]
        user_label_keys = self.get_user_keys()

        for current_key in current_labels.keys():
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
 
    def any_label_exists(self):
        ''' return whether any single label already exists '''
        current_labels = self.get()['results'][0]
        for label in self.labels:
            if label['key'] in current_labels:
                return True
        return False
            
    def get(self):
        '''return label information '''

        result = self._get(self.kind, self.name)
        if 'labels' in result['results'][0]['metadata']:

            label_list = result['results'][0]['metadata']['labels']
            result['results'][0] = label_list
        else:
            result['results'][0] = {}

        return result

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

    def cmd_template(self):
        ''' boilerplate oc command for modifying lables on this object '''
        cmd = ["-n", self.namespace, "--config", self.kubeconfig, "label", "node",
               self.name]
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
