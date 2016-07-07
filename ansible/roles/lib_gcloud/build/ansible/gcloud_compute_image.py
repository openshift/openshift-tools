# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud compute images'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str'),
            description=dict(default=None, type='str'),
            family=dict(default=None, type='str'),
            licenses=dict(default=None, type='list'),
            source_disk=dict(default=None, type='str'),
            source_disk_zone=dict(default=None, type='str'),
            source_uri=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )
    gimage = GcloudComputeImage(module.params['name'],
                                module.params['description'],
                                module.params['family'],
                                module.params['licenses'],
                                module.params['source_disk'],
                                module.params['source_disk_zone'],
                                module.params['source_uri'])

    state = module.params['state']

    api_rval = gimage.list_images(module.params['name'])

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
        if gimage.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = gimage.delete_image()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not gimage.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = gimage.create_image()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

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
