# pylint: skip-file

def main():
    '''
    ansible oc module for services
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            namespace=dict(default='default', type='str'),
            name=dict(default=None, type='str'),
            labels=dict(default=None, type='dict'),
            selector=dict(default=None, type='dict'),
            clusterip=dict(default=None, type='str'),
            portalip=dict(default=None, type='str'),
            ports=dict(default=None, type='list'),
            session_affinity=dict(default='None', type='str'),
            service_type=dict(default='ClusterIP', type='str'),
        ),
        supports_check_mode=True,
    )
    oc_svc = OCService(module.params['name'],
                       module.params['namespace'],
                       module.params['labels'],
                       module.params['selector'],
                       module.params['clusterip'],
                       module.params['portalip'],
                       module.params['ports'],
                       module.params['session_affinity'],
                       module.params['service_type'])

    state = module.params['state']

    api_rval = oc_svc.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval, state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oc_svc.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_svc.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")

        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oc_svc.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oc_svc.create()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_svc.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oc_svc.needs_update():
            api_rval = oc_svc.update()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_svc.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
