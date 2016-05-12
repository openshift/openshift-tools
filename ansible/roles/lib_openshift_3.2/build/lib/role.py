# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class RoleConfig(object):
    ''' Handle route options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 kubeconfig,
                 kind='Role',
                 rules=None):
        ''' constructor for handling route options '''
        self.kubeconfig = kubeconfig
        self.kind = kind
        self.name = sname
        self.namespace = namespace
        self.rules = rules
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a service as a dict '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = self.kind
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        self.data['rules'] = self.rules or []

# pylint: disable=too-many-instance-attributes
class Role(Yedit):
    ''' Class to wrap the oc command line tools '''
    rule_path = "rules"

    def __init__(self, content, kind='Role'):
        '''Role constructor'''
        super(Role, self).__init__(content=content)
        self.kind = kind

    def get_rules(self):
        ''' return cert '''
        return self.get(Role.rule_path) or []


class ClusterRole(Role):
    ''' Class to wrap the oc command line tools '''
    rule_path = "rules"

    def __init__(self, content, kind='ClusterRole'):
        '''ClusterRole constructor'''
        super(ClusterRole, self).__init__(content=content)
        self.kind = kind

    def get_rules(self):
        ''' return cert '''
        return self.get(Role.rule_path) or []
