# pylint: skip-file

def main():
    '''
    ansible oc module for route
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            name=dict(default=None, required=True, type='str'),
            namespace=dict(default=None, required=True, type='str'),
            tls_termination=dict(default=None, type='str'),
            cacert=dict(default=None, type='str'),
            cert=dict(default=None, type='str'),
            cert_key=dict(default=None, type='str'),
            service_name=dict(default=None, type='str'),
            host=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )

    rconfig = RouteConfig(module.params['name'],
                          module.params['namespace'],
                          module.params['kubeconfig'],
                          module.params['cacert'],
                          module.params['cert'],
                          module.params['cert_key'],
                          module.params['host'],
                          module.params['tls_termination'],
                          module.params['service_name'],
                         )
    oc_route = OCRoute(rconfig,
                       verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_route.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oc_route.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_route.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oc_route.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oc_route.create()

            # return the created object
            api_rval = oc_route.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oc_route.needs_update():
            api_rval = oc_route.update()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_route.get()

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
