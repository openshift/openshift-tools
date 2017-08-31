# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud compute disk labels'''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str', required=True),
            labels=dict(default=None, type='dict'),
            project=dict(default=None, type='str', required=True),
            zone=dict(default=None, type='str', required=True),
        ),
        #required_together=[['name', 'zone']],
        supports_check_mode=True,
    )

    results = GcloudComputeLabel.run_ansible(module.params, module.check_mode)

    if 'failed' in results:
        module.fail_json(**results)

    module.exit_json(**results)

if __name__ == '__main__':
    main()
