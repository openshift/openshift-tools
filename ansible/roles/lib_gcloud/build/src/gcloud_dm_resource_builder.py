# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudResourceBuilder(object):
    ''' Class to wrap the gcloud deployment manager '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 clusterid,
                 project,
                 region,
                 zone,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        #super(GcloudDeploymentManager, self).__init__()
        self.clusterid = clusterid
        self.project = project
        self.region = region
        self.zone = zone
        self.verbose = verbose

    def build_instance_resources(self,
                                 names,
                                 mtype,
                                 metadata,
                                 tags,
                                 disk_info,
                                 network_info,
                                 provisioning=False,
                                 service_accounts=None,
                                ):
        '''build instance resources and return them in a list'''

        results = []
        for _name in names:
            disks = [Disk(_name + '-' + disk['name'],
                          self.project,
                          self.zone,
                          disk['size'],
                          disk.get('disk_type', 'pd-standard'),
                          boot=disk.get('boot', False),
                          device_name=disk['device_name'],
                          image=disk.get('image', None)) for disk in disk_info]

            inst_disks = []
            for disk in disks:
                if disk.boot:
                    inst_disks.append(disk.get_instance_disk())
                else:
                    inst_disks.append(disk.get_supplement_disk())
                    results.append(disk)

            nics = []
            for nic in network_info:
                _nic = NetworkInterface(_name + 'nic',
                                        self.project,
                                        self.zone,
                                        nic['network'],
                                        nic['subnetwork'],
                                        nic.get('access_config_name', None),
                                        nic.get('access_config_type', None))

                nics.append(_nic.get_instance_interface())

            if provisioning:
                metadata['new_provision'] = 'True'

            inst = VMInstance(_name,
                              self.project,
                              self.zone,
                              mtype,
                              metadata,
                              tags,
                              inst_disks,
                              nics,
                              service_accounts)
            results.append(inst)

        return results

    def build_health_check(self, rname, desc, interval, h_thres, port, timeout, unh_thres, req_path):
        '''create health check resource'''
        return HealthCheck(rname,
                           self.project,
                           self.zone,
                           desc,
                           interval,
                           h_thres,
                           port,
                           timeout,
                           unh_thres,
                           req_path)

    def build_subnetwork(self, rname, ip_cidr_range, region, network):
        '''build subnetwork and return it'''
        return Subnetwork(rname, self.project, self.zone, ip_cidr_range, region, network)

    def build_target_pool(self, rname, desc, region, checks, instances, affin=None):
        '''build target pool resource and return it'''
        return TargetPool(rname, self.project, self.zone, desc, region, checks, instances, affin)

    def build_network(self, rname, desc, auto_create=False):
        '''build network resource and return it'''
        return Network(rname, self.project, self.zone, desc, auto_create)

    def build_address(self, rname, desc, region):
        '''build address resource and return it'''
        return Address(rname, self.project, self.zone, desc, region)

    def build_forwarding_rules(self, rules):
        '''build forwarding rule resources and return them'''
        resources = []
        for rule in rules:
            resources.append(ForwardingRule(rule['name'], self.project, self.zone,
                                            rule['description'], rule['IPAddress'],
                                            rule['IPProtocol'], rule['region'],
                                            rule['portRange'], rule['target']))
        return resources

    def build_firewall_rules(self, rules):
        '''build firewall resources and return them'''
        resources = []
        for rule in rules:
            resources.append(FirewallRule(rule['name'], self.project, self.zone,
                                          rule['description'], rule['network'],
                                          rule['allowed'], rule.get('targetTags', []),
                                          rule['sourceRanges']))
        return resources

    def build_disks(self, disks):
        '''build disk resources and return it'''
        results = []
        for disk in disks:
            results.append(Disk(disk['name'],
                                self.project,
                                self.zone,
                                disk['size'],
                                disk.get('disk_type', 'pd-standard'),
                                boot=disk.get('boot', False),
                                device_name=disk['device_name'],
                                image=disk.get('image', None)))
        return results

    def build_pv_disks(self, disk_size_info):
        '''build disk resources for pvs and return them
           disk_size_count:
           - size: 1
             count: 5
           - size: 5
           - count: 10
        '''
        results = []
        for size_count in disk_size_info:
            size = size_count['size']
            count = size_count['count']
            d_type = size_count.get('disk_type', 'pd-standard')
            for idx in range(1, int(count) + 1):
                results.append(Disk('pv-%s-%dg-%d' % (self.project, size, idx),
                                    self.project,
                                    self.zone,
                                    size,
                                    disk_type=d_type,
                                    boot=False,
                                    device_name='pv_%dg%d' % (size, idx),
                                    image=None))
        return results

    def build_storage_buckets(self, bucket_names):
        ''' create the resource for storage buckets'''
        results = []
        for b_name in bucket_names:
            results.append(Bucket(b_name, self.project, self.zone))

        return results
