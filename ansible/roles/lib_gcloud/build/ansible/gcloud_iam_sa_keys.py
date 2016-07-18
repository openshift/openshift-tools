# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud iam service-account keys'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str', choices=['present', 'absent', 'list']),
            service_account_name=dict(required=True, type='str'),
            key_format=dict(type='str', choices=['p12', 'json']),
            key_id=dict(default=None, type='str'),
            display_name=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )

    gcloud = GcloudIAMServiceAccountKeys(module.params['service_account_name'],
                                         module.params['key_format'])

    state = module.params['state']

    #####
    # Get
    #####
    if state == 'list':
        api_rval = gcloud.list_service_account_keys()

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="list")

        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed a delete.')

        api_rval = gcloud.delete_service_account_key(module.params['key_id'])

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=True, results=api_rval, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed a create.')

        # Create it here
        outputfile = '/tmp/glcoud_iam_sa_keys'
        api_rval = gcloud.create_service_account_key(outputfile)

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
