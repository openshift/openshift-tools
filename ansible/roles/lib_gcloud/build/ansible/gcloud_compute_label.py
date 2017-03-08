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

    compute_labels = GcloudComputeLabel(module.params['project'],
                                        module.params['zone'],
                                        module.params['labels'],
                                        module.params['name'],
                                       )

    state = module.params['state']

    api_rval = compute_labels.get_labels()

    #####
    # Get
    #####
    if state == 'list':
        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="list")

        module.exit_json(changed=False, results=api_rval, state="list")

    ########
    # Delete
    ########
    if state == 'absent':

       api_rval = compute_labels.delete_labels()

       if module.check_mode:
           module.exit_json(changed=False, msg='Would have performed a delete.')

       if 'returncode' in api_rval and api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="absent")

       if "no_deletes_needed" in api_rval:
           module.exit_json(changed=False, state="absent", msg=api_rval)

       module.exit_json(changed=True, results=api_rval, state="absent")

    ########
    # Create
    ########
    if state == 'present':

       api_rval = compute_labels.create_labels()

       if module.check_mode:
           module.exit_json(changed=False, msg='Would have performed a create.')

       if 'returncode' in api_rval and api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval, state="present")

       if "no_creates_needed" in api_rval:
           module.exit_json(changed=False, state="present", msg=api_rval)


       module.exit_json(changed=True, results=api_rval, state="present")

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
