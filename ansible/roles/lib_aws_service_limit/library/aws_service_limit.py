#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
#
# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
''' module for retrieving AWS service limits '''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import boto3_conn, \
                                     ec2_argument_spec, \
                                     HAS_BOTO3, \
                                     camel_dict_to_snake_dict, \
                                     get_aws_connection_info

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['development'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: lib_aws_service_limit
short_description: Provides AWS service limits as facts.
requirements:
  - boto3 >= 1.4.4
  - python >= 2.6
description:
    - Provides AWS service limits and account attributes as facts.
author: "Brett Lentz (@blentz)"
extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Note: Only AWS EC2 and Trusted Advisor is currently supported

# Note: The data from Trusted Advisor needs to be periodically refreshed. This
# module does not include a mechanism to refresh TA reports.

# Lists EC2 account attributes and TA service limits
- aws_service_limit:
'''

RETURN = '''
aws_account_attributes:
  description: "List of account attributes"
  returned: always
  sample:
    - supported-platforms: string
    - max-elastic-ips: integer
  type: list
aws_service_limits:
  description: "List of service limits"
  returned: always
  sample:
    - current_use: integer,
      limit_value: integer,
      limit_name: string,
      region: string,
      service: string,
      status: string
  type: list
'''

try:
    import botocore
except ImportError:
    pass  # will be detected by imported HAS_BOTO3

def account_attributes(ec2):
    '''
    Collects and arranges EC2 account attributes

    Param: ec2 connection object
    Returns: list of account attributes; each attribute is a dict
    '''

    # Gather results from EC2
    attr_results = ec2.describe_account_attributes()

    # strip out extraneous info
    attributes = []
    for attr in attr_results['AccountAttributes']:
        if len(attr['AttributeValues']) < 2:
            attributes.append({attr['AttributeName']:attr['AttributeValues'][0]['AttributeValue']})
        else:
            vals = []
            for val in attr['AttributeValues']:
                vals.append(val['AttributeValue'])
            attributes.append({attr['AttributeName'] : vals})
    return attributes

def service_limits(tr_adv):
    '''
    Collects and arranges Trusted Advisor service limits

    Param: support connection object
    Returns: list of service limits; each service limit is a dict containing:
        - region (string)
        - service (string)
        - limit_name (string)
        - limit_value (integer)
        - current_value (integer)
        - status (string)
    '''
    # look up the service limits ID
    ta_query = tr_adv.describe_trusted_advisor_checks(language='en')
    service_limits_id = None
    for check in ta_query['checks']:
        if check['name'] == "Service Limits":
            service_limits_id = check['id']

    # Gather results from Trusted Advisor
    ta_results = tr_adv.describe_trusted_advisor_check_result(checkId=service_limits_id)

    # extract limits from the most recent TA report
    limits = []
    for res in ta_results['result']['flaggedResources']:
        limits.append({'region' : res['metadata'][0],
                       'service' : res['metadata'][1],
                       'limit_name' : res['metadata'][2],
                       'limit_value' : res['metadata'][3],
                       'current_value' : res['metadata'][4],
                       'status' : res['metadata'][5]})
    return limits

def main():
    """
    get service limits
    :return:
    """

    result = {}

    # Including ec2 argument spec
    module = AnsibleModule(argument_spec=ec2_argument_spec(),
                           supports_check_mode=True)

    # Set up connection
    region, ec2_url, aws_connect_params = get_aws_connection_info(module,
                                                                  boto3=HAS_BOTO3)

    # Set up connection
    if region:
        try:
            ec2_conn = boto3_conn(module,
                                  conn_type='client',
                                  resource='ec2',
                                  region=region,
                                  endpoint=ec2_url,
                                  **aws_connect_params)

            # region is hard-coded because there is only one support endpoint.
            # see: https://docs.aws.amazon.com/general/latest/gr/rande.html#awssupport_region
            ta_conn = boto3_conn(module,
                                 conn_type='client',
                                 resource='support',
                                 region='us-east-1',
                                 endpoint=ec2_url,
                                 **aws_connect_params)

        except (botocore.exceptions.NoCredentialsError,
                botocore.exceptions.ProfileNotFound) as exc:
            # pylint: disable=no-member
            module.fail_json(msg=exc.message,
                             exception=traceback.format_exc(),
                             **camel_dict_to_snake_dict(exc.response))
    else:
        module.fail_json(msg="AWS region must be specified (like: us-east-1)")

    result['aws_account_attributes'] = account_attributes(ec2_conn)
    result['aws_service_limits'] = service_limits(ta_conn)

    # Send exit
    module.exit_json(msg="Retrieved ec2 account attributes.", ansible_facts=result)

if __name__ == '__main__':
    main()
