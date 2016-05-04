# pylint: skip-file

#pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for user
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            namespace=dict(default='default', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            username=dict(default=None, type='str'),
            full_name=dict(default=None, type='str'),
            # setting groups for user data seems to have no effect
            # group membership is stored in 'oc get groups' data
            # so ignore user passed groups
            #groups=dict(default=None, type='list'),
        ),
        supports_check_mode=True,
    )

    uconfig = UserConfig(module.params['namespace'],
                         module.params['kubeconfig'],
                         module.params['username'],
                         module.params['full_name'],
                        )

    oc_user = OCUser(uconfig, verbose=module.params['debug'])
    state = module.params['state']

    api_rval = oc_user.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oc_user.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_user.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oc_user.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oc_user.create()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_user.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oc_user.needs_update():
            api_rval = oc_user.update()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            orig_cmd = api_rval['cmd']
            # return the created object
            api_rval = oc_user.get()
            # overwrite the get/list cmd
            api_rval['cmd'] = orig_cmd

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
