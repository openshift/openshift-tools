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
            kind=dict(default='dc', choices=['dc', 'rc', 'pods'], type='str'),
            namespace=dict(default='default', type='str'),
            vol_name=dict(default=None, type='str'),
            name=dict(default=None, type='str'),
            mount_type=dict(default=None,
                            choices=['emptydir', 'hostpath', 'secret', 'pvc'],
                            type='str'),
            mount_path=dict(default=None, type='str'),
            # secrets require a name
            secret_name=dict(default=None, type='str'),
            # pvc requires a size
            claim_size=dict(default=None, type='str'),
            claim_name=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )
    oc_volume = OCVolume(module.params['kind'],
                         module.params['name'],
                         module.params['namespace'],
                         module.params['vol_name'],
                         module.params['mount_path'],
                         module.params['mount_type'],
                         # secrets
                         module.params['secret_name'],
                         # pvc
                         module.params['claim_size'],
                         module.params['claim_name'],
                         kubeconfig=module.params['kubeconfig'],
                         verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_volume.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oc_volume.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_volume.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oc_volume.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oc_volume.put()

            # return the created object
            api_rval = oc_volume.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oc_volume.needs_update():
            api_rval = oc_volume.put()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_volume.get()

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
