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
            secrets=dict(default=None, type='list'),
            service_account=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )
    oc_secret_add = OCSecretAdd(module.params['secrets'],
                                module.params['service_account'],
                                module.params['namespace'],
                                kubeconfig=module.params['kubeconfig'],
                                verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_secret_add.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        for secret in module.params.get('secrets', []):
            if oc_secret_add.exists(secret):

                if module.check_mode:
                    module.exit_json(changed=False, msg='Would have performed a delete.')

                api_rval = oc_secret_add.delete()

                module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        for secret in module.params.get('secrets', []):
            if not oc_secret_add.exists(secret):

                if module.check_mode:
                    module.exit_json(changed=False, msg='Would have performed a create.')

                # Create it here
                api_rval = oc_secret_add.put()

                if api_rval['returncode'] != 0:
                    module.fail_json(msg=api_rval)

                # return the created object
                api_rval = oc_secret_add.get()

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
