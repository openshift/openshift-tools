# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#def parse_metadata(path):
#    '''grab the metadata from file so we can compare it with existing metadata'''
#
#    if not os.path.exists(path):
#        raise GcloudComputeProjectInfoError('Error finding path to metadata file [%s]' % path)
#
#    metadata = {}
#
#    with open(path) as _metafd:
#        for line in _metafd.readlines():
#            if line:
#                key, value = line.split(':')
#            metadata[key] = value
#
#
#    return metadata

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud compute project_info'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            metadata=dict(default=None, type='dict'),
            metadata_from_file=dict(default=None, type='dict'),
            remove_keys=dict(default=None, type='list'),
            remove_all=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['metadata', 'metadata_from_file'],
                            ['remove_keys', 'remove_all'],
                           ]
    )


    #metadata = module.params['metadata']
    #if not metadata and module.params['metadata_from_file']:
    #    # read in metadata and parse it
    #    metadata = {}
    #    for _, val in module.params['metadata_from_file'].items():
    #        metadata.update(parse_metadata(val))

    gcloud = GcloudComputeProjectInfo(module.params['metadata'],
                                      module.params['metadata_from_file'],
                                      module.params.get('remove_keys', None),
                                     )

    state = module.params['state']

    api_rval = gcloud.list_metadata()

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
        if module.params['remove_all'] or gcloud.keys_exist():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = gcloud.delete_metadata(remove_all=module.params['remove_all'])

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not gcloud.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = gcloud.create_metadata()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        # update
        elif gcloud.needs_update():
            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed an update.')

            api_rval = gcloud.create_metadata()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present|update")

        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudComputeImage('rhel-7-base-2016-06-10')
#    print gcloud.list_images()


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
