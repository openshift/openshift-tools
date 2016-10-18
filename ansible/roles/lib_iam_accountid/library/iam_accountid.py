#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# pylint: skip-file
DOCUMENTATION = '''
---
module: oo_iam_account
version_added: "1.9"
short_description: simple module to get current AWS account
description:
     - Get AWS account and user from the ACCESS KEY used
options:
  state:
    description:
      - list the aws account info
    required: false
    default: 'list'
'''

# Thank you to iAcquire for sponsoring development of this module.

EXAMPLES = '''
# Basic Usage
- oo_iam_account:
    state: list
  register: iam_info

'''
try:
    import boto3
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

def get_aws_accountid():
    ''' get the aws account id '''

    iam_user = {}
    iam_user_raw = boto3.client('iam').get_user()['User']['Arn']

    iam_user['accountid'] = iam_user_raw.split(':')[4]
    iam_user['user'] = iam_user_raw.split(':')[5].split('/')[1]

    return iam_user

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            state = dict(default='list')
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO:
        module.fail_json(msg='boto3 required for this module')

    if module.params.get('state') == 'list':
        iam_user = get_aws_accountid()

        module.exit_json(changed=False, iam_user=iam_user)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

main()
