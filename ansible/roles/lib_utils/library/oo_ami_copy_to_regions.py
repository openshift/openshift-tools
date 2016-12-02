#!/usr/bin/python
"""ansible module for ec2 ami copy to all regions"""
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4

DOCUMENTATION = '''
---
module: aos_ami_copy_to_regions
short_description: this module copies an ami out to all regions
description:
- this module accepts an ami id and copies it to all regions
options:
  ami_name:
    description:
    - name of the ami
    required: false
    default: none
    aliases: []
  ami_id:
    description:
    - id of the ami
    required: false
    default: none
    aliases: []
  region:
    description:
    - the region where the ami exists
    required: false
    default: us-east-1
    aliases: []
'''
EXAMPLES = '''
# perform a list on the enabled repos
- aos_ami_copy_to_regions:
    ami_id: ami-xxxxxx
    region: us-east-1
  register: repos
'''

import boto.ec2

class AMICopy(object):
    """simple wrapper class for rhsm repos"""

    regions_to_copy = ['us-east-1',
                       'us-west-1',
                       'us-west-2',
                       'eu-west-1',
                       'ap-southeast-1',
                       'ap-southeast-2',
                       'eu-central-1',
                       'eu-central-1',
                      ]

    def __init__(self, aid=None, name=None, region='us-east-1'):
        '''constructor for amicopy class'''
        self._ami = None
        self.ami_id = aid
        self.ami_name = name
        self.region = region
        self.conn = boto.ec2.connect_to_region(region)

    @property
    def ami(self):
        '''property for ami'''
        if self._ami == None:
            images = self.get_images()
            self._ami = images[0]
        return self._ami

    @ami.setter
    def ami(self, inc):
        '''setter for ami'''
        self._ami = inc

    def get_images(self, filters=None):
        '''Return images based on a filter'''
        filt = {}
        if filters:
            filt = filters

        elif self.ami_id:
            filt['image_id'] = self.ami_id
        else:
            filt['name'] = self.ami_name

        return self.conn.get_all_images(filters=filt)

    def copy_to_region(self):
        """verify that the enabled repos are enabled"""
        ami_dict = {}
        for region in AMICopy.regions_to_copy:
            conn = boto.ec2.connect_to_region(region)
            ami = conn.get_all_images(filters={'name': self.ami.name})
            if not ami:
                ami = conn.copy_image(self.region, self.ami.id)
                ami_dict[region] = ami.image_id
            else:
                ami_dict[region] = ami[0].id

        return ami_dict

    @staticmethod
    def run_ansible(module):
        """run the ansible code"""
        amicopy = AMICopy(module.params.get('ami_id', None),
                          module.params.get('ami_name', None),
                          module.params['region'],
                         )

        # Step 1: Get the current ami name
        images = amicopy.get_images()
        if len(images) == 0:
            return {'msg': 'Unable to find ami with id or name.', 'rc': 0}

        amicopy.ami = images[0]

        # Step 2: if we are state=list, return the ami
        if module.params['state'] == 'list':
            module.exit_json(changed=False, ami=amicopy.ami, rc=0)

        # Step 2: if we are state=present, copy out the ami
        # Since ami doesn't have a sha or identifier other than name, we check name
        elif module.params['state'] == 'present':

            # Step 3: we need to set our repositories
            results = amicopy.copy_to_region()

            # Everything went ok, no changes were made
            if not results:
                module.exit_json(changed=False, results=results, rc=0)

            module.exit_json(changed=True, results=results, rc=0)

        module.fail_json(msg="unsupported state.", rc=1)

def main():
    """Create the ansible module and run the ansible code"""
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['list', 'present'], type='str'),
            ami_id=dict(default=None, type='str'),
            ami_name=dict(default=None, type='str'),
            region=dict(default='us-east-1', choices=AMICopy.regions_to_copy, type='str'),
            query=dict(default='all', choices=['all', 'enabled', 'disabled']),
        ),
        supports_check_mode=False,
    )

    # call the ansible function
    AMICopy.run_ansible(module)

if __name__ == '__main__':
# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import
# import module snippets
    from ansible.module_utils.basic import *
    main()
