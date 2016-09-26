# pylint: skip-file

def main():
    '''
    ansible oadm module for manage-node
    '''

    module = AnsibleModule(
        argument_spec=dict(
            debug=dict(default=False, type='bool'),
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            node=dict(default=None, type='list'),
            selector=dict(default=None, type='str'),
            pod_selector=dict(default=None, type='str'),
            schedulable=dict(default=None, type='bool'),
            list_pods=dict(default=False, type='bool'),
            evacuate=dict(default=False, type='bool'),
            dry_run=dict(default=False, type='bool'),
            force=dict(default=False, type='bool'),
            grace_period=dict(default=None, type='int'),
        ),
        mutually_exclusive=[["selector", "node"], ['evacuate', 'list_pods'], ['list_pods', 'schedulable']],
        required_one_of=[["node", "selector"]],

        supports_check_mode=True,
    )

    nconfig = ManageNodeConfig(module.params['kubeconfig'],
                               {'node': {'value': module.params['node'], 'include': True},
                                'selector': {'value': module.params['selector'], 'include': True},
                                'pod_selector': {'value': module.params['pod_selector'], 'include': True},
                                'schedulable': {'value': module.params['schedulable'], 'include': True},
                                'list_pods': {'value': module.params['list_pods'], 'include': True},
                                'evacuate': {'value': module.params['evacuate'], 'include': True},
                                'dry_run': {'value': module.params['dry_run'], 'include': True},
                                'force': {'value': module.params['force'], 'include': True},
                                'grace_period': {'value': module.params['grace_period'], 'include': True},
                               })


    oadm_mn = ManageNode(nconfig)
    # Run the oadm manage-node commands
    results = None
    changed = False
    if module.params['schedulable'] != None:
        results = oadm_mn.schedulable()
        changed = True

    if module.params['evacuate']:
        results = oadm_mn.evacuate()
        changed = True
    elif module.params['list_pods']:
        results = oadm_mn.list_pods()

    if not results or results['returncode'] != 0:
        module.fail_json(msg=results)

    module.exit_json(changed=changed, results=results, state="present")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *
main()
