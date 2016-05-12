# pylint: skip-file

# pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for services
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str', choices=['present']),
            debug=dict(default=False, type='bool'),
            namespace=dict(default='default', type='str'),
            template_name=dict(default=None, type='str'),
            params=dict(default=None, type='dict'),
            create=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
    )
    ocprocess = OCProcess(module.params['namespace'],
                          module.params['template_name'],
                          module.params['params'],
                          module.params['create'],
                          kubeconfig=module.params['kubeconfig'],
                          verbose=module.params['debug'])

    state = module.params['state']

    if state == 'present':
        # Create it here
        api_rval = ocprocess.process()
        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=True, results=api_rval, state="present")


    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
