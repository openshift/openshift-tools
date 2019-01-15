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
    register: calculated_subnets

  - debug:
      msg: "{{ item }}"
    with_items:
    - "{{ calculated_subnets.results }}"

  - name: set the vpc network space
    set_fact:
      openshift_aws_vpc:
        name: "{{ openshift_clusterid }}"
        cidr: 172.35.0.0/16
        subnets: "{{ calculated_subnets.results }}"

'''


def calc_subnets(module, cidr_block, num_of_subnets, num_avail_zones_in_region, region_name, availability_zones, multi_az):
    max_hosts_per_subnet = 2048
    min_hosts_per_subnet = 14
    ip = netaddr.IPNetwork(cidr_block)
    num_of_hosts_per_subnet = 0
    results = {}
    az_subnets = []

    if len(availability_zones) == 0:
        if module is None:
            print("No availability zones available for provided instance types.")
            return results
        else:
            module.fail_json(msg='No availability zones available for provided instance types.')

    if ip.size < min_hosts_per_subnet:
        if module is None:
            print("CIDR block is too small.")
            return results
        else:
            module.fail_json(msg='CIDR block is too small.')

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

    if multi_az:
        if num_avail_zones_in_region >= num_of_subnets:
            subnets = subnets[:3]
        else:
            if module is None:
                print("Not enough AZs found to support multi-AZ deployment")
                return results
            else:
                module.fail_json(msg='Not enough AZs found to support multi-AZ deployment')
    else:
        subnets = subnets[:1]


    for idx, subnet in enumerate(subnets):
        az_subnets.append({"cidr": str(subnet), "az": availability_zones[idx]})

    results = {region_name: az_subnets}

    return results

def is_reserved_instance_offered_in_az(boto_client, availability_zone, instance_type):

    response = boto_client.describe_reserved_instances_offerings(AvailabilityZone=availability_zone,
                                                                 Filters=[
                                                                     {
                                                                         'Name': 'availability-zone',
                                                                         'Values': [
                                                                             availability_zone,
                                                                         ]
                                                                     },
                                                                     {
                                                                         'Name': 'instance-type',
                                                                         'Values': [
                                                                             instance_type,
                                                                         ]
                                                                     },
                                                                 ],
                                                                 InstanceType=instance_type,
                                                                 IncludeMarketplace=False)

    return len(response['ReservedInstancesOfferings']) > 0


def instance_types_available_in_az(boto_client, availability_zone, master_node_instance_type, infra_node_instance_type, compute_node_instance_type):
    return (is_reserved_instance_offered_in_az(boto_client, availability_zone, master_node_instance_type) and
            is_reserved_instance_offered_in_az(boto_client, availability_zone, infra_node_instance_type) and
            is_reserved_instance_offered_in_az(boto_client, availability_zone, compute_node_instance_type))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            cidr_block=dict(required=True, type='str'),
            region=dict(default=None, required=True, type='str'),
            aws_access_key_id=dict(default=None, type='str'),
            aws_secret_access_key=dict(default=None, type='str'),
            number_of_subnets=dict(default=3, choices=[1, 3], type='int'),
            multi_az=dict(default=False, required=False, type='bool'),
            master_node_instance_type=dict(default=None, required=True, type='str'),
            infra_node_instance_type=dict(default=None, required=True, type='str'),
            compute_node_instance_type=dict(default=None, required=True, type='str'),
        ),
        supports_check_mode=True
    )

    cidr_block = module.params.get('cidr_block')
    region_name = module.params.get('region')
    aws_access_key_id = module.params.get('aws_access_key_id')
    aws_secret_access_key = module.params.get('aws_secret_access_key')
    number_of_subnets = module.params.get('number_of_subnets')
    multi_az = module.params.get('multi_az')
    master_node_instance_type = module.params.get('master_node_instance_type')
    infra_node_instance_type =  module.params.get('infra_node_instance_type')
    compute_node_instance_type = module.params.get('compute_node_instance_type')

    if aws_access_key_id and aws_secret_access_key:
        boto3.setup_default_session(aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)
    else:
        boto3.setup_default_session(region_name=region_name)

    boto_client = boto3.client('ec2')
    response = boto_client.describe_availability_zones()
    availability_zones = []

    for zone in response['AvailabilityZones']:
        if zone['State'] == 'available':
            if instance_types_available_in_az(boto_client, zone['ZoneName'], master_node_instance_type, infra_node_instance_type, compute_node_instance_type):
                availability_zones.append(zone['ZoneName'])

    num_avail_zones_in_region = len(response['AvailabilityZones'])
    results = calc_subnets(module, cidr_block, number_of_subnets, num_avail_zones_in_region, region_name, availability_zones, multi_az)
    module.exit_json(changed=False, ansible_facts={}, results=results)


if __name__ == '__main__':
    # pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import
    from ansible.module_utils.basic import *

    main()
