# pylint: skip-file

def main():
    '''
    ansible oc module for registry
    '''

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present', 'absent']),
            debug=dict(default=False, type='bool'),
            namespace=dict(default='default', type='str'),
            name=dict(default=None, required=True, type='str'),

            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            credentials=dict(default='/etc/origin/master/openshift-registry.kubeconfig', type='str'),
            images=dict(default=None, type='str'),
            latest_image=dict(default=False, type='bool'),
            labels=dict(default=None, type='list'),
            ports=dict(default=['5000'], type='list'),
            replicas=dict(default=1, type='int'),
            selector=dict(default=None, type='str'),
            service_account=dict(default='registry', type='str'),
            mount_host=dict(default=None, type='str'),
            registry_type=dict(default='docker-registry', type='str'),
            template=dict(default=None, type='str'),
            volume=dict(default='/registry', type='str'),
            env_vars=dict(default=None, type='dict'),
            volume_mounts=dict(default=None, type='list'),
            edits=dict(default=None, type='dict'),
        ),
        mutually_exclusive=[["registry_type", "images"]],

        supports_check_mode=True,
    )

    rconfig = RegistryConfig(module.params['name'],
                             module.params['namespace'],
                             module.params['kubeconfig'],
                             {'credentials': {'value': module.params['credentials'], 'include': True},
                              'default_cert': {'value': None, 'include': True},
                              'images': {'value': module.params['images'], 'include': True},
                              'latest_image': {'value': module.params['latest_image'], 'include': True},
                              'labels': {'value': module.params['labels'], 'include': True},
                              'ports': {'value': ','.join(module.params['ports']), 'include': True},
                              'replicas': {'value': module.params['replicas'], 'include': True},
                              'selector': {'value': module.params['selector'], 'include': True},
                              'service_account': {'value': module.params['service_account'], 'include': True},
                              'registry_type': {'value': module.params['registry_type'], 'include': False},
                              'mount_host': {'value': module.params['mount_host'], 'include': True},
                              'volume': {'value': module.params['mount_host'], 'include': True},
                              'template': {'value': module.params['template'], 'include': True},
                              'env_vars': {'value': module.params['env_vars'], 'include': False},
                              'volume_mounts': {'value': module.params['volume_mounts'], 'include': False},
                              'edits': {'value': module.params['edits'], 'include': False},
                             })


    ocregistry = Registry(rconfig)

    state = module.params['state']

    ########
    # Delete
    ########
    if state == 'absent':
        if not ocregistry.exists():
            module.exit_json(changed=False, state="absent")

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed a delete.')

        api_rval = ocregistry.delete()
        module.exit_json(changed=True, results=api_rval, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not ocregistry.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            api_rval = ocregistry.create()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if not ocregistry.needs_update():
            module.exit_json(changed=False, state="present")

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed an update.')

        api_rval = ocregistry.update()

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
