#!/usr/bin/env python
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|

'''
   GcloudCLI class that wraps the oc commands in a subprocess
'''

import string
import random
import json
import os
import yaml
import shutil
import subprocess
import atexit

class GcloudCLIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class GcloudCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self, credentials=None, verbose=False):
        ''' Constructor for OpenshiftCLI '''
        self.credentials = credentials
        self.verbose = verbose

    def _create_image(self, image_name, image_info):
        '''create an image name'''
        cmd = ['compute', 'images', 'create', image_name]
        for key, val in image_info.items():
            if val:
                cmd.extend(['--%s' % key, val])

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _delete_image(self, image_name):
        '''delete image by name '''
        cmd = ['compute', 'images', 'delete', image_name]
        if image_name:
            cmd.extend(['describe', image_name])
        else:
            cmd.append('list')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_images(self, image_name=None):
        '''list images.
           if name is supplied perform a describe and return
        '''
        cmd = ['compute', 'images']
        if image_name:
            cmd.extend(['describe', image_name])
        else:
            cmd.append('list')

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _list_deployments(self, simple=True):
        '''list deployments by name '''
        cmd = ['deployment-manager', 'deployments', 'list']
        if simple:
            cmd.append('--simple-list')
        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _delete_deployment(self, dname):
        '''list deployments by name '''
        cmd = ['deployment-manager', 'deployments', 'delete', dname, '-q']
        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _create_deployment(self, dname, config=None, opts=None):
        ''' create a deployment'''
        cmd = ['deployment-manager', 'deployments', 'create', dname]
        if config:
            if isinstance(config, dict):
                config = Utils.create_file(dname, config)

            if isinstance(config, str) and os.path.exists(config):
                cmd.extend(['--config=%s' % config])

        if opts:
            for key, val in opts.items():
                cmd.append('--%s=%s' % (key, val))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def _update_deployment(self, dname, config=None, opts=None):
        ''' create a deployment'''
        cmd = ['deployment-manager', 'deployments', 'update', dname]
        if config:
            if isinstance(config, dict):
                config = Utils.create_file(dname, config)

            if isinstance(config, str) and os.path.exists(config):
                cmd.extend(['--config=%s' % config])

        if opts:
            for key, val in opts.items():
                cmd.append('--%s=%s' % (key, val))

        return self.gcloud_cmd(cmd, output=True, output_type='raw')

    def gcloud_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for gcloud '''
        cmds = ['/usr/bin/gcloud']

        cmds.extend(cmd)

        rval = {}
        results = ''
        err = None

        if self.verbose:
            print ' '.join(cmds)

        proc = subprocess.Popen(cmds,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env={})

        proc.wait()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        rval = {"returncode": proc.returncode,
                "results": results,
                "cmd": ' '.join(cmds),
               }

        if proc.returncode == 0:
            if output:
                if output_type == 'json':
                    try:
                        rval['results'] = json.loads(stdout)
                    except ValueError as err:
                        if "No JSON object could be decoded" in err.message:
                            err = err.message
                elif output_type == 'raw':
                    rval['results'] = stdout

            if self.verbose:
                print stdout
                print stderr

            if err:
                rval.update({"err": err,
                             "stderr": stderr,
                             "stdout": stdout,
                             "cmd": cmds
                            })

        else:
            rval.update({"stderr": stderr,
                         "stdout": stdout,
                         "results": {},
                        })

        return rval

################################################################################
# utilities and helpers for generation
################################################################################
class Utils(object):
    ''' utilities for openshiftcli modules '''

    COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

    @staticmethod
    def create_file(rname, data, ftype='yaml'):
        ''' create a file in tmp with name and contents'''
        path = os.path.join('/tmp', rname)
        with open(path, 'w') as fds:
            if ftype == 'yaml':
                fds.write(yaml.safe_dump(data, default_flow_style=False))

            elif ftype == 'json':
                fds.write(json.dumps(data))
            else:
                fds.write(data)

        # Register cleanup when module is done
        atexit.register(Utils.cleanup, [path])
        return path

    @staticmethod
    def global_compute_url(project, collection, rname):
        '''build the global compute url for a resource'''
        return ''.join([Utils.COMPUTE_URL_BASE, 'projects/', project, '/global/', collection, '/', rname])

    @staticmethod
    def zonal_compute_url(project, zone, collection, rname):
        '''build the zone compute url for a resource'''
        return ''.join([Utils.COMPUTE_URL_BASE, 'projects/', project, '/zones/', zone, '/', collection, '/', rname])

    @staticmethod
    def generate_random_name(size):
        '''generate a random string of lowercase and digits the length of size'''
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))


    @staticmethod
    def cleanup(files):
        '''Clean up on exit '''
        for sfile in files:
            if os.path.exists(sfile):
                if os.path.isdir(sfile):
                    shutil.rmtree(sfile)
                elif os.path.isfile(sfile):
                    os.remove(sfile)


class GCPResource(object):
    '''Object to represent a gcp resource'''

    def __init__(self, rname, rtype, project, zone):
        '''constructor for gcp resource'''
        self._name = rname
        self._type = rtype
        self._project = project
        self._zone = zone

    @property
    def name(self):
        '''property for name'''
        return self._name

    @property
    def type(self):
        '''property for type'''
        return self._type

    @property
    def project(self):
        '''property for project'''
        return self._project

    @property
    def zone(self):
        '''property for zone'''
        return self._zone

class Address(GCPResource):
    '''Object to represent a gcp address'''

    resource_type = "compute.v1.address"

    # pylint: disable=too-many-arguments
    def __init__(self, rname, project, zone, desc, region):
        '''constructor for gcp resource'''
        super(Address, self).__init__(rname, Address.resource_type, project, zone)
        self._desc = desc
        self._region = region

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Address.resource_type,
                'properties': {'description': self.description,
                               'region': self.region,
                              }
               }


# pylint: disable=too-many-instance-attributes
class Disk(GCPResource):
    '''Object to represent a gcp disk'''

    resource_type = "compute.v1.disk"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 size,
                 disk_type='pd-standard', #pd-ssd, local-ssd
                 persistent=True,
                 auto_delete=True,
                 boot=False,
                 device_name=None,
                 image=None,
                ):
        '''constructor for gcp resource'''
        super(Disk, self).__init__(rname,
                                   Disk.resource_type,
                                   project,
                                   zone)
        if persistent:
            self._persistent = 'PERSISTENT'
        else:
            self._persistent = 'SCRATCH'

        self._size = size
        self._boot = boot
        self._image = image
        self._device_name = device_name
        self._disk_type = disk_type
        self._disk_url = None
        self._auto_delete = auto_delete

    @property
    def persistent(self):
        '''property for resource if boot device is persistent'''
        return self._persistent

    @property
    def device_name(self):
        '''property for resource device name'''
        return self._device_name

    @property
    def boot(self):
        '''property for resource is a boot device'''
        return self._boot

    @property
    def image(self):
        '''property for resource image'''
        return self._image

    @property
    def disk_type(self):
        '''property for resource disk type'''
        return self._disk_type

    @property
    def disk_url(self):
        '''property for resource disk url'''
        if self._disk_url == None:
            self._disk_url = Utils.zonal_compute_url(self.project, self.zone, 'diskTypes', self.disk_type)
        return self._disk_url

    @property
    def size(self):
        '''property for resource disk size'''
        return self._size

    @property
    def auto_delete(self):
        '''property for resource disk auto delete'''
        return self._auto_delete

    def get_instance_disk(self):
        '''return in vminstance format'''
        return {'deviceName': self.device_name,
                'type': self.persistent,
                'autoDelete': self.auto_delete,
                'boot': self.boot,
                'sizeGb': self.size,
                'initializeParams': {'diskName': self.name,
                                     'sourceImage': Utils.global_compute_url(self.project,
                                                                             'images',
                                                                             self.image)
                                    }
               }

    def get_supplement_disk(self):
        '''return in vminstance format'''
        return {'deviceName': self.device_name,
                'type': self.persistent,
                'source': '$(ref.%s.selfLink)' % self.name,
                'autoDelete': self.auto_delete,
               }

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Disk.resource_type,
                'properties': {'zone': self.zone,
                               'sizeGb': self.size,
                               'type': self.disk_url,
                               'autoDelete': self.auto_delete,
                              }
               }


# pylint: disable=too-many-instance-attributes
class FirewallRule(GCPResource):
    '''Object to represent a gcp forwarding rule'''

    resource_type = "compute.v1.firewall"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 network,
                 allowed,
                 target_tags,
                 source_ranges=None,
                 source_tags=None,
                ):
        '''constructor for gcp resource'''
        super(FirewallRule, self).__init__(rname,
                                           FirewallRule.resource_type,
                                           project,
                                           zone)
        self._desc = desc
        self._allowed = allowed
        self._network = '$(ref.%s.selfLink)' % network
        self._target_tags = target_tags

        self._source_ranges = []
        if source_ranges:
            self._source_ranges = source_ranges

        self._source_tags = []
        if source_tags:
            self._source_tags = source_tags

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def target_tags(self):
        '''property for resource target_tags'''
        return self._target_tags

    @property
    def source_tags(self):
        '''property for resource source_tags'''
        return self._source_tags

    @property
    def source_ranges(self):
        '''property for resource source_ranges'''
        return self._source_ranges

    @property
    def allowed(self):
        '''property for resource allowed'''
        return self._allowed

    @property
    def network(self):
        '''property for resource network'''
        return self._network

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': FirewallRule.resource_type,
                'properties': {'description': self.description,
                               'network': self.network,
                               'sourceRanges': self.source_ranges,
                               'sourceTags': self.source_tags,
                               'allowed': self.allowed,
                               'targetTags': self.target_tags,
                              }
               }


# pylint: disable=too-many-instance-attributes
class ForwardingRule(GCPResource):
    '''Object to represent a gcp forwarding rule'''

    resource_type = "compute.v1.forwardingRule"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 ip_address,
                 protocol,
                 region,
                 port_range,
                 target,
                ):
        '''constructor for gcp resource'''
        super(ForwardingRule, self).__init__(rname, ForwardingRule.resource_type, project, zone)
        self._desc = desc
        self._region = region
        self._ip_address = '$(ref.%s.selfLink)' % ip_address
        self._protocol = protocol
        self._port_range = port_range
        self._target = '$(ref.%s.selfLink)' % target

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    @property
    def ip_address(self):
        '''property for resource ip_address'''
        return self._ip_address

    @property
    def protocol(self):
        '''property for resource protocol'''
        return self._protocol

    @property
    def port_range(self):
        '''property for resource port_range'''
        return self._port_range

    @property
    def target(self):
        '''property for resource target'''
        return self._target

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': ForwardingRule.resource_type,
                'properties': {'description': self.description,
                               'region': self.region,
                               'IPAddress': self.ip_address,
                               'IPProtocol': self.protocol,
                               'portRange': self.port_range,
                               'target': self.target,
                              }
               }


# pylint: disable=too-many-instance-attributes
class HealthCheck(GCPResource):
    '''Object to represent a gcp health check'''

    resource_type = "compute.v1.httpHealthCheck"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 interval_secs,
                 healthy_threshold,
                 port,
                 timeout_secs,
                 unhealthy_threshold,
                ):
        '''constructor for gcp resource'''
        super(HealthCheck, self).__init__(rname, HealthCheck.resource_type, project, zone)
        self._desc = desc
        self._interval_secs = interval_secs
        self._healthy_threshold = healthy_threshold
        self._unhealthy_threshold = unhealthy_threshold
        self._port = port
        self._timeout_secs = timeout_secs

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def interval_secs(self):
        '''property for resource interval_secs'''
        return self._interval_secs

    @property
    def timeout_secs(self):
        '''property for resource timeout_secs'''
        return self._timeout_secs

    @property
    def healthy_threshold(self):
        '''property for resource healthy_threshold'''
        return self._healthy_threshold

    @property
    def unhealthy_threshold(self):
        '''property for resource unhealthy_threshold'''
        return self._unhealthy_threshold

    @property
    def port(self):
        '''property for resource port'''
        return self._port

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': HealthCheck.resource_type,
                'properties': {'description': self.description,
                               'checkIntervalSec': self.interval_secs,
                               'port': self.port,
                               'healthyThreshold': self.healthy_threshold,
                               'unhealthyThreshold': self.unhealthy_threshold,
                               'timeoutSec': 5,
                              }
               }


# pylint: disable=too-many-instance-attributes,interface-not-implemented
class NetworkInterface(GCPResource):
    '''Object to represent a gcp disk'''

    #resource_type = "compute.v1."
    resource_type = ''

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 network,
                 subnet,
                 access_config_name=None,
                 access_config_type=None,
                ):
        '''constructor for gcp resource'''
        super(NetworkInterface, self).__init__(rname,
                                               NetworkInterface.resource_type,
                                               project,
                                               zone)
        if not access_config_name and not access_config_type:
            self._access_config = None
        else:
            self._access_config = [{'name': access_config_name or 'default',
                                    'type': access_config_type or 'ONE_TO_ONE_NAT'}]
        self._network_link = '$(ref.%s.selfLink)' % network
        self._subnet_link = '$(ref.%s.selfLink)' % subnet
        self._network = network
        self._subnet = subnet

    @property
    def access_config(self):
        '''property for resource if boot device is persistent'''
        return self._access_config

    @property
    def network(self):
        '''property for resource network'''
        return self._network

    @property
    def subnet(self):
        '''property for resource subnet'''
        return self._subnet

    def get_instance_interface(self):
        '''return in vminstance format'''
        return {'accessConfigs': self.access_config,
                'network': self._network_link,
                'subnetwork': self._subnet_link,
               }


# pylint: disable=too-many-instance-attributes
class Network(GCPResource):
    '''Object to represent a gcp Network'''

    resource_type = "compute.v1.network"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 auto_create_subnets,
                ):
        '''constructor for gcp resource'''
        super(Network, self).__init__(rname,
                                      Network.resource_type,
                                      project,
                                      zone)
        self._desc = desc
        self._auto_create_subnets = auto_create_subnets

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def auto_create_subnets(self):
        '''property for resource auto_create_subnets'''
        return self._auto_create_subnets

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Network.resource_type,
                'properties': {'description': self.description,
                               'autoCreateSubnetworks': self.auto_create_subnets,
                              }
               }


# pylint: disable=too-many-instance-attributes
class Subnetwork(GCPResource):
    '''Object to represent a gcp subnetwork'''

    resource_type = "compute.v1.subnetwork"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 ip_cidr_range,
                 region,
                 network,
                ):
        '''constructor for gcp resource'''
        super(Subnetwork, self).__init__(rname,
                                         Subnetwork.resource_type,
                                         project,
                                         zone)
        self._ip_cidr_range = ip_cidr_range
        self._region = region
        self._network = '$(ref.%s.selfLink)' % network

    @property
    def ip_cidr_range(self):
        '''property for resource ip_cidr_range'''
        return self._ip_cidr_range

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    @property
    def network(self):
        '''property for resource network'''
        return self._network

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Subnetwork.resource_type,
                'properties': {'ipCidrRange': self.ip_cidr_range,
                               'network': self.network,
                               'region': self.region,
                              }
               }


# pylint: disable=too-many-instance-attributes
class TargetPool(GCPResource):
    '''Object to represent a gcp targetPool'''

    resource_type = "compute.v1.targetPool"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 desc,
                 region,
                 health_checks=None, #pd-ssd, local-ssd
                 instances=None,
                 session_affinity=None,
                ):
        '''constructor for gcp resource'''
        super(TargetPool, self).__init__(rname,
                                         TargetPool.resource_type,
                                         project,
                                         zone)
        self._region = region
        self._desc = desc
        self._session_affinity = session_affinity

        self._instances = instances
        self._health_checks = health_checks

        self._instance_refs = None
        self._health_checks_refs = None

    @property
    def description(self):
        '''property for resource description'''
        return self._desc

    @property
    def region(self):
        '''property for resource region'''
        return self._region

    @property
    def session_affinity(self):
        '''property for resource session_affinity'''
        return self._session_affinity

    @property
    def instances(self):
        '''property for resource instances'''
        return self._instances

    @property
    def health_checks(self):
        '''property for resource health_checks'''
        return self._health_checks

    @property
    def instance_refs(self):
        '''property for resource instance references type'''
        if self._instance_refs == None:
            self._instance_refs = ['$(ref.%s.selfLink)' % inst for inst in self.instances]
        return self._instance_refs

    @property
    def health_checks_refs(self):
        '''property for resource health_checks'''
        if self._health_checks_refs == None:
            self._health_checks_refs = ['$(ref.%s.selfLink)' % check for check in self.health_checks]
        return self._health_checks_refs

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': TargetPool.resource_type,
                'properties': {'description': self.description,
                               'healthChecks': self.health_checks_refs,
                               'instances': self.instance_refs,
                               'sessionAffinity': 'NONE',
                               'region': self.region,
                              }
               }


# pylint: disable=too-many-instance-attributes
class VMInstance(GCPResource):
    '''Object to represent a gcp instance'''

    resource_type = "compute.v1.instance"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 machine_type,
                 metadata,
                 disks,
                 network_interfaces,
                ):
        '''constructor for gcp resource'''
        super(VMInstance, self).__init__(rname, VMInstance.resource_type, project, zone)
        self._machine_type = machine_type
        self._machine_type_url = None
        self._metadata = []
        if metadata and isinstance(metadata, dict):
            self._metadata = {'items': [{'key': key, 'value': value} for key, value in metadata.items()]}
        elif metadata and isinstance(metadata, list):
            self._metadata = [{'key': label['key'], 'value': label['value']} for label in metadata]
        self._disks = disks
        self._network_interfaces = network_interfaces
        self._properties = None

    @property
    def network_interfaces(self):
        '''property for resource machine network_interfaces '''
        return self._network_interfaces

    @property
    def machine_type(self):
        '''property for resource machine type '''
        return self._machine_type

    @property
    def machine_type_url(self):
        '''property for resource machine type url'''
        if self._machine_type_url == None:
            self._machine_type_url = Utils.zonal_compute_url(self.project, self.zone, 'machineTypes', self.machine_type)
        return  self._machine_type_url

    @property
    def metadata(self):
        '''property for resource metadata'''
        return self._metadata

    @property
    def disks(self):
        '''property for resource disks'''
        return self._disks

    @property
    def properties(self):
        '''property for holding the properties'''
        if self._properties == None:
            self._properties = {'zone': self.zone,
                                'machineType': self.machine_type_url,
                                'metadata': self.metadata,
                                'disks': self.disks,
                                'networkInterfaces': self.network_interfaces,
                               }
        return self._properties

    def to_resource(self):
        '''return the resource representation'''
        return {'name': self.name,
                'type': VMInstance.resource_type,
                'properties': self.properties,
               }

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
        ''' Constructor for OCVolume '''
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
                                 disk_info,
                                 network_info,
                                 provisioning=False,
                                ):
        '''build instance resources and return them in a list'''

        results = []
        for _name in names:
            disks = [Disk(_name + '-' + disk['name'],
                          self.project,
                          self.zone,
                          disk['size'],
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
                              inst_disks,
                              nics)
            results.append(inst)

        return results

    def build_health_check(self, rname, desc, interval, h_thres, port, timeout, unh_thres):
        '''create health check resource'''
        return HealthCheck(rname,
                           self.project,
                           self.zone,
                           desc,
                           interval,
                           h_thres,
                           port,
                           timeout,
                           unh_thres)

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
                                boot=disk.get('boot', False),
                                device_name=disk['device_name'],
                                image=disk.get('image', None)))
        return results
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
            provisioning=dict(default=False, type='bool'),
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
                                                             properties['network_interfaces'],
                                                             module.params['provisioning']))

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
