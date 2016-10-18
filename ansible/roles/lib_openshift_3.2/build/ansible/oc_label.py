# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

#pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for labels
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list', 'add']),
            debug=dict(default=False, type='bool'),
            kind=dict(default=None, type='str', required=True,
                          choices=['node', 'pod']),
            name=dict(default=None, type='str'),
            namespace=dict(default=None, type='str'),
            labels=dict(default=None, type='list'),
            selector=dict(default=None, type='str'),
            host=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
        mutually_exclusive = (['name', 'selector']),
    )

    oc_label = OCLabel(module.params['name'],
                       module.params['namespace'],
                       module.params['kind'],
                       module.params['kubeconfig'],
                       module.params['labels'],
                       module.params['selector'],
                       verbose=module.params['debug'])

    state = module.params['state']
    name = module.params['name']
    selector = module.params['selector']

    api_rval = oc_label.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    #######
    # Add
    #######
    if state == 'add':
        if not (name or selector):
            module.fail_json( msg="Parameter 'name' or 'selector' is required if state == 'add'")
        if not oc_label.all_user_labels_exist():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed an addition.')
            api_rval = oc_label.add()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="add")

        module.exit_json(changed=False, state="add")

    ########
    # Delete
    ########
    if state == 'absent':
        if not (name or selector):
            module.fail_json( msg="Parameter 'name' or 'selector' is required if state == 'absent'")

        if oc_label.any_label_exists():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_label.delete()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="absent")

        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Update
        ########
        if not (name or selector):
            module.fail_json( msg="Parameter 'name' or 'selector' is required if state == 'present'")
        # if all the labels passed in don't already exist
        # or if there are currently stored labels that haven't
        # been passed in
        if not oc_label.all_user_labels_exist() or \
           oc_label.extra_current_labels():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have made changes.')

            api_rval = oc_label.replace()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_label.get()

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
