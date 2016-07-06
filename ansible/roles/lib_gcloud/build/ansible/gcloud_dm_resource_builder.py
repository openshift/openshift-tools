# pylint: skip-file
# vim: expandtab:tabstop=4:shiftwidth=4

def get_names(rname, count):
    '''generate names and return them in a list'''
    return ['%s-%s' % (rname, Utils.generate_random_name(5)) for _ in range(count)]

#pylint: disable=too-many-branches
def main():
    ''' ansible module for gcloud deployment-manager deployments '''
    module = AnsibleModule(
        argument_spec=dict(
            # credentials
            clusterid=dict(required=True, type='str'),
            accountid=dict(required=True, type='str'),
            sublocation=dict(required=True, type='str'),
            zone=dict(required=True, type='str'),
            health_checks=dict(default=[], type='list'),
            firewall_rules=dict(default=[], type='list'),
            forwarding_rules=dict(default=[], type='list'),
            instances=dict(default=None, type='dict'),
            instance_counts=dict(default=None, type='dict'),
            networks=dict(default=[], type='list'),
            target_pools=dict(default=[], type='list'),
            subnetworks=dict(default=[], type='list'),
            addresses=dict(default=[], type='list'),
            disks=dict(default=[], type='list'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
        ),
        required_together=[
            ['instances', 'target_pools'],
        ],
        supports_check_mode=True,
    )
    # TODO
    gcloud = GcloudResourceBuilder(module.params['accountid'],
                                   module.params['clusterid'],
                                   module.params['sublocation'],
                                   module.params['zone'])
    names = {}
    resources = []

    state = module.params['state']

    ########
    # generate resources
    ########
    if state == 'present':
        names = {}
        names['master'] = get_names(module.params['clusterid'] + '-master',
                                    int(module.params['instance_counts'].get('master', 0)))
        names['infra'] = get_names(module.params['clusterid'] + '-node-infra',
                                   int(module.params['instance_counts'].get('infra', 0)))
        names['compute'] = get_names(module.params['clusterid'] + '-node-compute',
                                     int(module.params['instance_counts'].get('compute', 0)))

        # Health Checks
        for health_check in module.params.get('health_checks', []):
            resources.append(gcloud.build_health_check(health_check['name'],
                                                       health_check['description'],
                                                       health_check['checkIntervalSec'],
                                                       health_check['healthyThreshold'],
                                                       health_check['port'],
                                                       health_check['timeoutSec'],
                                                       health_check['unhealthyThreshold']))

        # Address
        for address in module.params.get('addresses', []):
            resources.append(gcloud.build_address(address['name'], address['description'], address['region']))

        # target pool
        for target_pool in module.params.get('target_pools', []):
            instances = None
            if 'master' in target_pool['name']:
                instances = names['master']
            elif 'infra' in target_pool['name']:
                instances = names['infra']
            elif 'compute' in target_pool['name']:
                instances = names['compute']

            resources.append(gcloud.build_target_pool(target_pool['name'],
                                                      target_pool['description'],
                                                      target_pool['region'],
                                                      target_pool['targetpool_healthchecks'],
                                                      instances))
        # forwarding rules
        resources.extend(gcloud.build_forwarding_rules(module.params.get('forwarding_rules', [])))

        # network
        for network in module.params.get('networks', []):
            resources.append(gcloud.build_network(network['name'],
                                                  network['description'],
                                                  network['autocreate_subnets']))

        # subnetwork
        for subnetwork in module.params.get('subnetworks', []):
            resources.append(gcloud.build_subnetwork(subnetwork['name'],
                                                     subnetwork['ipCidrRange'],
                                                     subnetwork['region'],
                                                     subnetwork['network']))

        # firewall rules
        resources.extend(gcloud.build_firewall_rules(module.params.get('firewall_rules', [])))

        # instances
        for hosttype in module.params.get('instance_counts', {}).keys():
            properties = module.params['instances'][hosttype]
            resources.extend(gcloud.build_instance_resources(names[hosttype],
                                                             properties['machine_type'],
                                                             properties['metadata'],
                                                             properties['disk_info'],
                                                             properties['network_interfaces']))

        # disks
        resources.extend(gcloud.build_disks(module.params.get('disks', [])))

        # Return resources in their deployment-manager resource form.
        resources = [res.to_resource() for res in resources if isinstance(res, GCPResource)]
        module.exit_json(failed=False, changed=False, results={'resources': resources})

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

#if __name__ == '__main__':
#    gcloud = GcloudResourceBuilder('optestgcp', 'optestgcp', 'us-east1-c')
#    print gcloud.list_deployments()


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
