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
            kind=dict(default='rc', choices=['dc', 'rc', 'pods'], type='str'),
            namespace=dict(default='default', type='str'),
            name=dict(default=None, required=True, type='str'),
            env_vars=dict(default=None, type='dict'),
            list_all=dict(default=False, type='bool'),
        ),
        mutually_exclusive=[["content", "files"]],

        supports_check_mode=True,
    )
    ocenv = OCEnv(module.params['namespace'],
                  module.params['kind'],
                  module.params['env_vars'],
                  resource_name=module.params['name'],
                  list_all=module.params['list_all'],
                  kubeconfig=module.params['kubeconfig'],
                  verbose=module.params['debug'])

    state = module.params['state']

    api_rval = ocenv.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        for key in module.params.get('env_vars', {}).keys():
            if ocenv.resource.exists_env_key(key):

                if module.check_mode:
                    module.exit_json(changed=False, msg='Would have performed a delete.')
                api_rval = ocenv.delete()
                module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        for key, value in module.params.get('env_vars', {}).items():
            if not ocenv.value_exists(key, value):

                if module.check_mode:
                    module.exit_json(changed=False, msg='Would have performed a create.')
                # Create it here
                api_rval = ocenv.put()

                if api_rval['returncode'] != 0:
                    module.fail_json(msg=api_rval)

                # return the created object
                api_rval = ocenv.get()

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
