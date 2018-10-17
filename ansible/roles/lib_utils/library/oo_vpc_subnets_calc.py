#!/usr/bin/python
# vim: expandtab:tabstop=2:shiftwidth=2

import boto3
import netaddr
import math

''' vpc_subnets_calc module

    The purpose of this module is to cat the contents of a file into an Ansible fact for use later.
    
    
Test Playbook:
---
- hosts: localhost
  gather_facts: no
  tasks:
  - include_role:
      name: ../../roles/lib_utils
    static: true
  - oo_vpc_subnets_calc:
      cidr_block: "172.16.0.0/24"
      region: "us-east-1"
      number_of_subnets: 3
    register: out
  - debug:
      msg: "{{ item }}"
    with_items:
    - "{{ out.results }}"    
    
'''

def calc_subnets(module, cidr_block, num_of_subnets, num_avail_zones_in_region):
    max_hosts_per_subnet = 2048
    min_hosts_per_subnet = 14
    ip = netaddr.IPNetwork(cidr_block)
    num_of_hosts_per_subnet = 0
    results = []

    if ip.size < min_hosts_per_subnet:
        if module is None:
            module.fail_json(msg='CIDR block is too small.')
        else:
            print("CIDR block is too small.")
            return results

    if ip.size >= (max_hosts_per_subnet * 3) and num_avail_zones_in_region >= num_of_subnets:
        num_of_hosts_per_subnet = max_hosts_per_subnet
    else:
        num_of_hosts_per_subnet = int(ip.size / 4)

    if num_of_hosts_per_subnet >= max_hosts_per_subnet:
        num_of_hosts_per_subnet = max_hosts_per_subnet
    else:
        if num_of_hosts_per_subnet < min_hosts_per_subnet:
            num_of_hosts_per_subnet = min_hosts_per_subnet

    bits = 32 - int(round(math.log(num_of_hosts_per_subnet, 2)))
    subnets = list(ip.subnet(bits))

    if num_avail_zones_in_region >= num_of_subnets:
        subnets = subnets[:3]
    else:
        subnets = subnets[:1]

    for item in subnets:
        results.append(str(item)) 

    return results


def main():
    
    module = AnsibleModule(
        argument_spec=dict(
            cidr_block=dict(required=True, type='str'),
            region=dict(default=None, required=True, type='str'),
            aws_access_key_id=dict(default=None, type='str'),
            aws_secret_access_key=dict(default=None, type='str'),
            number_of_subnets=dict(default=3, choices=[1, 3], type='int'),
        ),
        supports_check_mode=True
    )

    cidr_block = module.params.get('cidr_block')
    region_name = module.params.get('region')
    aws_access_key_id = module.params.get('aws_access_key_id')
    aws_secret_access_key = module.params.get('aws_secret_access_key')
    number_of_subnets = module.params.get('number_of_subnets')

    if aws_access_key_id and aws_secret_access_key:
        boto3.setup_default_session(aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)
    else:
        boto3.setup_default_session(region_name=region_name)

    boto_client = boto3.client('ec2')
    response = boto_client.describe_availability_zones()
    num_avail_zones_in_region = len(response['AvailabilityZones'])
    results = calc_subnets(module, cidr_block, number_of_subnets, num_avail_zones_in_region)
    module.exit_json(changed=False, ansible_facts={}, results=results)


if __name__ == '__main__':
    # pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import
    from ansible.module_utils.basic import *

    main()
