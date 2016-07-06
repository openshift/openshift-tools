#!/usr/bin/env python

from gcloud_dm_resource_builder import *
import pprint
import yaml

def get_names(clusterid, hosttype, count):
    return ['%s-%s-%s' % (clusterid, hosttype, Utils.generate_random_name(5)) for idx in range(count)]

gcloud = GcloudResourceBuilder('optestgcp', 'optestgcp', 'us-east1-c')

###### DATA  #####
disk_info = [{'name': 'osdisk',
              'size': 40,
              'boot': True,
              'device_name': 'boot',
              'image': 'rhel-7-2016-06-10'},
             {'name': 'dockerdisk',
              'size': 100,
              'device_name': 'docker'
             }]
network_interfaces = [{'network': 'optestgcp',
                       'subnetwork': 'optestgcp-subnet1',
                       'access_config_name': 'external-nat',
                       'access_config_type': 'ONE_TO_ONE_NAT',
                      }]

hosttype = 'master'
clusterid = 'optestgcp'

master_names = get_names(clusterid, hosttype, 3)

resources = []
###### END DATA  #####
#health check
resources.append(gcloud.build_health_check('%s-%s-healthcheck' % (clusterid, hosttype),
                                           'Check https port 443',
                                           30,
                                           2,
                                           443,
                                           5,
                                           2))

#address
resources.append(gcloud.build_address('%s-%s-ip-address' % (clusterid, hosttype), 'Static IP of the Master LB', 'us-east1',))
#target pool
resources.append(gcloud.build_target_pool('%s-%s-targetpool' % (clusterid, hosttype),
                                          'load balancer for master nodes',
                                          'us-east1',
                                          ['%s-%s-healthcheck' % (clusterid, hosttype)],
                                          master_names))
#forwarding rule
forward_rules = [{'name': '%s-%s-forwarding-rule-443' % (clusterid, hosttype),
                  'desc': 'Port 443 forwarding rule for master',
                  'IPAddress': '%s-%s-ip-address' % (clusterid, hosttype),
                  'IPProtocol': 'TCP',
                  'region': 'us-east1',
                  'portRange': 443,
                  'target': '%s-%s-targetpool' % (clusterid, hosttype)}]
resources.extend(gcloud.build_forwarding_rules(forward_rules))
#network
resources.append(gcloud.build_network(clusterid, 'main network for cluster', False))
#subnetwork
resources.append(gcloud.build_subnetwork('%s-subnet1' % clusterid, "172.25.0.0/24", 'us-east1', clusterid))
#firewall rules
rules = [{'name': 'allow-internal-traffic',

          'desc': 'allow internal traffic',
          'network': 'optestgcp',
          'source_ranges': ["0.0.0.0/0"],
          'allowed': [{'IPProtocol': 'tcp'},
                      {'IPProtocol': 'udp'},
                      {'IPProtocol': 'icmp'},
                      ],
          'target_tags': [],
          }]
resources.extend(gcloud.build_firewall_rules(rules))

#master instances and instance disks
resources.extend(gcloud.build_instance_resources(master_names,
                                                 'g1-small',
                                                 {'clusterid': clusterid,
                                                  'hosttype': hosttype},
                                                 disk_info,
                                                 network_interfaces,
                                                ))

#pprint.pprint([res.to_resource() for res in resources])
print yaml.dump({'resources': [res.to_resource() for res in resources]}, default_flow_style=False)
