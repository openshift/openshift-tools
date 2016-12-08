# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud project policy'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str', choices=['present', 'absent', 'list']),
            project=dict(required=True, type='str'),
            member=dict(default=None, type='str'),
            member_type=dict(type='str', choices=['serviceAccount', 'user']),
            role=dict(default=None, type='str'),
            policy_data=dict(default=None, type='dict'),
            policy_path=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['policy_path', 'policy_data']],
    )

    gcloud = GcloudProjectPolicy(module.params['project'],
                                 module.params['role'],
                                 module.params['member'],
                                 module.params['member_type'])

    state = module.params['state']

    api_rval = gcloud.list_project_policy()

    #####
    # Get
    #####
    if state == 'list':

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="list")

        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if gcloud.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = gcloud.remove_project_policy()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="absent")

        module.exit_json(changed=False, results=api_rval, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if module.params['policy_data'] or module.params['policy_path']:


            if gcloud.needs_update(module.params['policy_data'], module.params['policy_path']):
                # perform set
                if module.check_mode:
                    module.exit_json(changed=False, msg='Would have performed a set policy.')

                api_rval = gcloud.set_project_policy(module.params['policy_data'], module.params['policy_path'])

                if api_rval['returncode'] != 0:
                    module.fail_json(msg=api_rval)

                module.exit_json(changed=True, results=api_rval, state="present")

            module.exit_json(changed=False, results=api_rval, state="present")


        if not gcloud.exists():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            api_rval = gcloud.add_project_policy()

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
