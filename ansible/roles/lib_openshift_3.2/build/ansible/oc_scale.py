# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

def main():
    '''
    ansible oc module for scaling
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'list']),
            debug=dict(default=False, type='bool'),
            kind=dict(default='dc', choices=['dc', 'rc'], type='str'),
            namespace=dict(default='default', type='str'),
            replicas=dict(default=None, type='int'),
            name=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )
    oc_scale = OCScale(module.params['name'],
                       module.params['namespace'],
                       module.params['replicas'],
                       module.params['kind'],
                       module.params['kubeconfig'],
                       verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_scale.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    if state == 'present':
        ########
        # Update
        ########
        if oc_scale.needs_update():
            api_rval = oc_scale.put()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_scale.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval['results'], state="present")

        module.exit_json(changed=False, results=api_rval['results'], state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
