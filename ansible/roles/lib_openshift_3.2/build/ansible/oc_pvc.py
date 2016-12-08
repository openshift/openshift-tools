# pylint: skip-file

#pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for pvc
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            name=dict(default=None, required=True, type='str'),
            namespace=dict(default=None, required=True, type='str'),
            volume_capacity=dict(default='1G', type='str'),
            access_modes=dict(default=None, type='list'),
        ),
        supports_check_mode=True,
    )

    pconfig = PersistentVolumeClaimConfig(module.params['name'],
                                          module.params['namespace'],
                                          module.params['kubeconfig'],
                                          module.params['access_modes'],
                                          module.params['volume_capacity'],
                                         )
    oc_pvc = OCPVC(pconfig, verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_pvc.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oc_pvc.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_pvc.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oc_pvc.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oc_pvc.create()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_pvc.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oc_pvc.pvc.is_bound() or oc_pvc.pvc.get_volume_name():
            api_rval['msg'] = '##### - This volume is currently bound.  Will not update - ####'
            module.exit_json(changed=False, results=api_rval, state="present")

        if oc_pvc.needs_update():
            api_rval = oc_pvc.update()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_pvc.get()

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
