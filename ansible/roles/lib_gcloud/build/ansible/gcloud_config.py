# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud config'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str',
                       choices=['present', 'list']),
            project=dict(default=None, type='str'),
            region=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['project', 'region']],
    )

    gcloud = GcloudConfig(module.params['project'],
                          module.params['region'],
                         )

    state = module.params['state']

    api_rval = gcloud.list_config()

    #####
    # Get
    #####
    if state == 'list':
        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="list")

        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Create
    ########
    if state == 'present':
        if gcloud.update():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed an update.')

            api_rval = gcloud.update()

            if 'returncode' in api_rval:
                if api_rval['returncode'] != 0:
                    module.fail_json(msg=api_rval)

                module.exit_json(changed=True, results=api_rval, state="present|update")

        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
