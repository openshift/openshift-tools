# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud deployment-manager deployments '''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            resources=dict(required=True, type='dict'),
            instance_counts=dict(default=None, type='dict'),
            existing_instance_names=dict(default=None, type='dict'),
            current_dm_config=dict(default=None, type='dict'),
            state=dict(default='present', type='str', choices=['present']),
        ),
        required_together=[
            ['existing_instance_names', 'instance_counts', 'resources'],
        ],
        supports_check_mode=True,
    )
    gcloud = GcloudResourceReconciler(module.params['resources']['resources'],
                                      module.params['instance_counts'],
                                      module.params['existing_instance_names'],
                                      module.params['current_dm_config'])

    state = module.params['state']

    orig_resources = copy.deepcopy(module.params['resources'])

    ########
    # generate resources
    ########
    if state == 'present':
        # Deployment manager has run but nothing is in the inventory
        if not module.params['existing_instance_names'] and module.params['current_dm_config']:
            raise GcloudResourceReconcilerError(\
             'Found current deployment manager config but no existing resource names.' + \
             'Please update inventory and rerun.')

        # No existing instance names passed so we cannot reconcile.
        if not module.params['existing_instance_names']:
            module.exit_json(changed=False, results=module.params['resources'], run_dm=True)

        inst_resources = gcloud.gather_instance_resources()

        gcloud.reconcile_count(inst_resources)

        results = gcloud.get_resources()

        if module.params['current_dm_config']:
            run_dm = gcloud.compare_dm_config_resources(module.params['current_dm_config']['resources'])

            if results == orig_resources:
                module.exit_json(changed=False, results=orig_resources, run_dm=run_dm)

            module.exit_json(changed=True, results=results, run_dm=run_dm)

        module.exit_json(changed=True, results=results, run_dm=True)

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudResourceReconciler(resources,
#                                      {'master': 1, 'infra': 2, 'compute': 4},
#                                      existing_instance_info)
#    resources = gcloud.gather_instance_resources()
#    gcloud.reconcile_count(resources)
#    print yaml.dump(gcloud.resources, default_flow_style=False)


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
