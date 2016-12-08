# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud compute disk labels'''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            disk_name=dict(default=None, type='str'),
            name_match=dict(default=None, type='str'),
            labels=dict(default=None, type='dict'),
            project=dict(default=False, type='str'),
            zone=dict(default=False, type='str'),
            creds=dict(default=None, type='dict'),
        ),
        required_one_of=[['disk_name', 'name_match']],
        supports_check_mode=True,
    )
    if module.params['disk_name']:
        disks = GcloudCLI().list_disks(zone=module.params['zone'], disk_name=module.params['disk_name'])['results']
        disks = [GcloudComputeDisk(module.params['project'],
                                   module.params['zone'],
                                   disk,
                                   module.params['creds']) for disk in disks]

    elif module.params['name_match']:
        regex = re.compile(module.params['name_match'])
        disks = []
        for disk in GcloudCLI().list_disks(zone=module.params['zone'])['results']:
            if regex.findall(disk['name']):
                gdisk = GcloudComputeDisk(module.params['project'],
                                          module.params['zone'],
                                          disk,
                                          module.params['creds'])
                disks.append(gdisk)

    else:
        module.fail_json(changed=False, msg='Please specify disk_name or name_match.')

    state = module.params['state']

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=disks, state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if len(disks) > 0:
            if not all([disk.has_labels(module.params['labels']) for disk in disks]):
                module.exit_json(changed=False, state="absent")

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')
            results = []
            for disk in disks:
                results.append(disk.delete_labels())
            module.exit_json(changed=True, results=results, state="absent")

        module.exit_json(changed=False, msg='No disks found.', state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not all([disk.has_labels(module.params['labels']) for disk in disks]):

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')
            # Create it here
            results = []
            for disk in disks:
                results.append(disk.set_labels(module.params['labels']))

            module.exit_json(changed=True, results=results, state="present")

        module.exit_json(changed=False, state="present")

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
