# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud compute zones'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='list', type='str',
                       choices=['list']),
            region=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )

    gcloud = GcloudComputeZones(module.params['region'])

    state = module.params['state']

    api_rval = gcloud.list_zones()

    #####
    # Get
    #####
    if state == 'list':
        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="list")

        module.exit_json(changed=False, results=api_rval['results'], state="list")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
