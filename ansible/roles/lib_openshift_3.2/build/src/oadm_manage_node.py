# pylint: skip-file

class ManageNodeException(Exception):
    ''' manage-node exception class '''
    pass

class ManageNodeConfig(OpenShiftCLIConfig):
    ''' ManageNodeConfig is a DTO for the manage-node command.'''
    def __init__(self, kubeconfig, node_options):
        super(ManageNodeConfig, self).__init__(None, None, kubeconfig, node_options)

# pylint: disable=too-many-instance-attributes
class ManageNode(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(ManageNode, self).__init__(None, config.kubeconfig)
        self.config = config

    def evacuate(self):
        ''' formulate the params and run oadm manage-node '''
        return self._evacuate(node=self.config.config_options['node']['value'],
                              selector=self.config.config_options['selector']['value'],
                              pod_selector=self.config.config_options['pod_selector']['value'],
                              dry_run=self.config.config_options['dry_run']['value'],
                             )

    def list_pods(self):
        ''' run oadm manage-node --list-pods'''
        results = self._list_pods(node=self.config.config_options['node']['value'],
                                  selector=self.config.config_options['selector']['value'],
                                  pod_selector=self.config.config_options['pod_selector']['value'],
                                 )
        if results['returncode'] != 0:
            return results

        # When a selector or node is matched it is returned along with the json.
        # We are going to split the results based on the regexp and then
        # load the json for each matching node.
        # Before we return we are going to loop over the results and pull out the node names.
        # {'node': [pod, pod], 'node': [pod, pod]}
        # 3.2 includes the following lines in stdout: "Listing matched pods on node:"
        all_pods = []
        if "Listing matched" in results['results']:
            listing_match = re.compile('\n^Listing matched.*$\n', flags=re.MULTILINE)
            pods = listing_match.split(results['results'])
            all_pods = [json.loads(pod)['items'] for pod in pods if pod]

        # 3.3 specific
        else:
            # this is gross but I filed a bug...
            # build our own json from the output.
            pods = re.split('\n}\n', results['results'])
            all_pods = []
            for pod in pods:
                if len(pod) == 0:
                    continue
                pods = json.loads(pod + "}")
                all_pods.append(pods['items'])

        rval = {}

        for i in range(len(all_pods)):
            if all_pods[i]:
                rval[all_pods[i][0]['spec']['nodeName']] = all_pods[i]

        results['results'] = rval

        return results

    def schedulable(self):
        '''oadm manage-node call for making nodes unschedulable'''
        return self._schedulable(node=self.config.config_options['node']['value'],
                                 selector=self.config.config_options['selector']['value'],
                                 schedulable=self.config.config_options['schedulable']['value'],
                                )

