# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud deployment-manager manifests '''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='list', type='str', choices=['list']),
            name=dict(default=None, type='str'),
            deployment=dict(required=True, default=None),
        ),
        supports_check_mode=True,
    )
    gconfig = GcloudDeploymentManagerManifests(module.params['deployment'],
                                               module.params['name'])

    state = module.params['state']

    api_rval = gconfig.list_manifests()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")


    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudDeploymentManager('optestgcp')
#    print gcloud.list_deployments()


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
