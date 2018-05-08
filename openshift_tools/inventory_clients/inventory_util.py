# vim: expandtab:tabstop=4:shiftwidth=4

"""This module comprises Aws specific utility functions."""

import os
import re
import subprocess
from distutils.version import LooseVersion
import ruamel.yaml as yaml

# Buildbot does not have multi_inventory installed
#pylint: disable=no-name-in-module
from openshift_tools.inventory_clients import multi_inventory

class ArgumentError(Exception):
    """This class is raised when improper arguments are passed."""

    def __init__(self, message):
        """Initialize an ArgumentError.

        Keyword arguments:
        message -- the exact error message being raised
        """
        super(ArgumentError, self).__init__()
        self.message = message

# pylint: disable=too-many-public-methods
class InventoryUtil(object):
    """This class contains the Inventory utility functions."""

    def __init__(self, host_type_aliases=None, use_cache=True):
        """Initialize the Inventory utility class.

        Keyword arguments:
        host_type_aliases -- a list of aliases to common host-types (e.g. ex-node)
        use_cache -- rely on cached inventory instead of querying for new inventory
        """

        self.cached = use_cache
        self.alias_lookup = {}
        host_type_aliases = host_type_aliases or {}

        self.host_type_aliases = host_type_aliases
        self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))

        self.setup_host_type_alias_lookup()
        self._inventory = None

    @property
    def inventory(self):
        """ Sets up a class property named inventory, this is the getter
        It will pull in the file if the property is empty, otherwise just returns the variable
        """
        if self._inventory is None:
            self._inventory = multi_inventory.MultiInventory(None).run()
        return self._inventory

    @staticmethod
    def get_cluster(name):
        """ return a cluster object """

        return Cluster(name)

    def setup_host_type_alias_lookup(self):
        """Sets up the alias to host-type lookup table."""
        for key, values in self.host_type_aliases.iteritems():
            for value in values:
                self.alias_lookup[value] = key

    def _get_tags_(self, regex):
        """ Searches for tags in the inventory and returns all of the tags
            found.

            Param: a compiled regular expression
            Returns: a List of tags
        """

        tags = []
        for key in self.inventory:
            matched = regex.match(key)
            if matched:
                tags.append(matched.group(1))

        tags.sort()
        return tags

    def get_clusters(self):
        """Searches for cluster tags in the inventory and returns all of the clusters found."""
        pattern = re.compile(r'^oo_clusterid_(.*)')
        return self._get_tags_(pattern)

    def get_environments(self):
        """Searches for env tags in the inventory and returns all of the envs found."""
        pattern = re.compile(r'^oo_environment_(.*)')
        return self._get_tags_(pattern)

    def get_host_types(self):
        """Searches for host-type tags in the inventory and returns all host-types found."""
        pattern = re.compile(r'^oo_hosttype_(.*)')
        return self._get_tags_(pattern)

    def get_sub_host_types(self):
        """Searches for sub-host-type tags in the inventory and returns all sub-host-types found."""
        pattern = re.compile(r'^oo_subhosttype_(.*)')
        return self._get_tags_(pattern)

    def get_security_groups(self):
        """Searches for security_groups in the inventory and returns all SGs found."""
        pattern = re.compile(r'^security_group_(.*)')
        return self._get_tags_(pattern)

    def build_host_dict_by_env(self, args=None):
        """Searches the inventory for hosts in an env and returns their hostvars."""
        args = args or []

        inst_by_env = {}
        for _, host in self.inventory['_meta']['hostvars'].items():
            # If you don't have an environment tag, we're going to ignore you
            if 'oo_environment' not in host:
                continue

            if host['oo_environment'] not in inst_by_env:
                inst_by_env[host['oo_environment']] = {}
            host_id = "%s:%s" % (host['oo_name'], host['oo_id'])
            inst_by_env[host['oo_environment']][host_id] = host

        return inst_by_env

    def print_host_types(self):
        """Gets the list of host types and aliases and outputs them in columns."""

        host_types = self.get_host_types()
        ht_format_str = "%35s"
        alias_format_str = "%-20s"
        combined_format_str = ht_format_str + "    " + alias_format_str

        print
        print combined_format_str % ('Host Types', 'Aliases')
        print combined_format_str % ('----------', '-------')

        for host_type in host_types:
            aliases = []
            if host_type in self.host_type_aliases:
                aliases = self.host_type_aliases[host_type]
                print combined_format_str % (host_type, ", ".join(aliases))
            else:
                print  ht_format_str % host_type
        print

    def print_cluster_list(self):
        """Gets the list of clusters and outputs them"""
        clusters = self.get_clusters()

        for cluster in clusters:
            print cluster

    def resolve_host_type(self, host_type):
        """Converts a host-type alias into a host-type.

        Keyword arguments:
        host_type -- The alias or host_type to look up.

        Example (depends on aliases defined in config file):
            host_type = ex-node
            returns: openshift-node
        """
        if self.alias_lookup.has_key(host_type):
            return self.alias_lookup[host_type]
        return host_type

    @staticmethod
    def gen_version_tag(ver):
        """Generate the version tag
        """
        return "oo_version_%s" % ver

    @staticmethod
    def gen_clusterid_tag(clu):
        """Generate the clusterid tag
        """
        return "oo_clusterid_%s" % clu

    @staticmethod
    def gen_env_tag(env):
        """Generate the environment tag
        """
        return "oo_environment_%s" % env

    def gen_host_type_tag(self, host_type, version):
        """Generate the host type tag
        """
        if version == '2':
            host_type = self.resolve_host_type(host_type)
        return "oo_hosttype_%s" % host_type

    @staticmethod
    def gen_sub_host_type_tag(sub_host_type):
        """Generate the host type tag
        """
        return "oo_subhosttype_%s" % sub_host_type

    # This function uses all of these params to perform a filters on our host inventory.
    # pylint: disable=too-many-arguments
    def get_host_list(self, clusters=None, host_type=None, sub_host_type=None, envs=None, version=None):
        """Get the list of hosts from the inventory using host-type and environment
        """
        retval = set([])
        envs = envs or []

        retval.update(self.inventory.get('all_hosts', []))

        if clusters:
            cluster_hosts = set([])
            if len(clusters) > 1:
                for cluster in clusters:
                    clu_tag = InventoryUtil.gen_clusterid_tag(cluster)
                    cluster_hosts.update(self.inventory.get(clu_tag, []))
            else:
                cluster_hosts.update(self.inventory.get(InventoryUtil.gen_clusterid_tag(clusters[0]), []))

            retval.intersection_update(cluster_hosts)

        if envs:
            env_hosts = set([])
            if len(envs) > 1:
                for env in envs:
                    env_tag = InventoryUtil.gen_env_tag(env)
                    env_hosts.update(self.inventory.get(env_tag, []))
            else:
                env_hosts.update(self.inventory.get(InventoryUtil.gen_env_tag(envs[0]), []))

            retval.intersection_update(env_hosts)

        if host_type:
            retval.intersection_update(self.inventory.get(self.gen_host_type_tag(host_type, version), []))

        if sub_host_type:
            retval.intersection_update(self.inventory.get(self.gen_sub_host_type_tag(sub_host_type), []))

        if version != 'all':
            retval.intersection_update(self.inventory.get(InventoryUtil.gen_version_tag(version), []))

        return list(retval)

    def convert_to_ip(self, hosts):
        """convert a list of host names to ip addresses"""

        if not isinstance(hosts, list):
            hosts = [hosts]

        ips = []
        for host in hosts:
            ips.append(self.inventory['_meta']['hostvars'][host]['oo_public_ip'])

        return ips

    @staticmethod
    def get_cluster_variable(cluster, variable):
        """ return an inventory variable that is common to a cluster"""

        cluster = InventoryUtil.get_cluster(cluster)

        return cluster.get_variable(variable)

    def get_node_variable(self, host, variable):
        """ return an inventory variable from a host"""

        if host in self.inventory['_meta']['hostvars'] and variable in self.inventory['_meta']['hostvars'][host]:
            return self.inventory['_meta']['hostvars'][host][variable]

        return None

class Cluster(object):
    """ This is a class to acces data about an Ops cluster """

    def __init__(self, name):
        """ Init the cluster class """

        self._name = name
        self._openshift_version = None
        self._docker_version = None
        self.inventory = multi_inventory.MultiInventory(None).run()
        self._master_config = None

    def __str__(self):
        """ str representation of Cluster """

        return self._name

    def __repr__(self):
        """ repr representation of Cluster """

        return self._name

    @property
    def name(self):
        """ cluster name property """

        return self._name

    @property
    def location(self):
        """ cluster location property """

        return self.get_variable('oo_location')

    @property
    def sublocation(self):
        """ cluster sublocation property """

        return self.get_variable('oo_sublocation')

    @property
    def environment(self):
        """ cluster environment property """

        return self.get_variable('oo_environment')

    @property
    def deployment(self):
        """ cluster deployment property """

        return self.get_variable('oo_deployment')

    @property
    def account(self):
        """ cluster account property """

        return self.get_variable('oo_account')

    @property
    def accountid(self):
        """ cluster account property """

        return self.get_variable('oo_accountid')

    @property
    def test_cluster(self):
        """ cluster cluster property """

        return bool(self.get_variable('oo_test_cluster'))

    @property
    def primary_master(self):
        """ return the first master """

        primary_master = list(set(self.inventory["oo_master_primary"]) &
                              set(self.inventory["oo_clusterid_" + self._name]))[0]

        return primary_master

    @property
    def cluster_nodes(self):
        """ return the number of nodes - infra and compute """

        cluster_nodes = self.inventory["oo_clusterid_" + self._name]

        return cluster_nodes

    @property
    def node_count(self):
        """ return the number of nodes - infra and compute """

        cluster_compute_nodes = list(set(self.inventory["oo_hosttype_node"]) &
                             set(self.inventory["oo_clusterid_" + self._name]))

        return len(cluster_compute_nodes)

    @property
    def scalegroup_node_count(self):
        """ return the number of scalegroup nodes - infra and compute """

        sg_cluster_nodes = list(set(self.inventory["oo_hosttype_node"]) &
                                set(self.inventory["oo_scalegroup_True"]) &
                                set(self.inventory["oo_clusterid_" + self._name]))

        return len(sg_cluster_nodes)


    @property
    def master_config(self):
        """ This is the master_config.yaml file stored as a dict """

        if not self._master_config:
            master_config_yaml = self.run_cmd_on_master("/usr/bin/cat /etc/origin/master/master-config.yaml",
                                                        strip=False)
            self._master_config = yaml.load(master_config_yaml)

        return self._master_config

    @staticmethod
    def set_version(version):
        """ manipulate the version variable """

        os_version = {}
        version_split = version.split('.')

        os_version['version_release'] = version
        os_version['version'] = version.split('-')[0]
        os_version['short'] = '.'.join(version_split[0:2])
        os_version['short_underscore'] = os_version['short'].replace(".", "_")
        os_version['release'] = version.split('-')[1]
        os_version['version_release_no_git'] = version.split('.git')[0]

        # Let's do the wierdness to set full version begin
        if LooseVersion(os_version['short']) < LooseVersion('3.6'):
            os_version['full'] = os_version['short']
        elif os_version['short'] == '3.6':
            os_version['full'] = os_version['version']
        else:
            if "-0.git" in os_version['version_release']:
                os_version['full'] = os_version['version_release_no_git']
            else:
                os_version['full'] = os_version['version']

        return os_version

    @property
    def openshift_version(self):
        """ return a dict of openshift_version """

        if not self._openshift_version:
            self._openshift_version = {}
            version = self.run_cmd_on_master("rpm -q --queryformat '%{VERSION}-%{RELEASE}' \
                                                           atomic-openshift")
            self._openshift_version = Cluster.set_version(version)

        return self._openshift_version

    def get_variable(self, variable):
        """ return an inventory variable that is common to a cluster"""

        variables = []
        for host in self.inventory['oo_clusterid_' + self.name]:
            if variable in self.inventory['_meta']['hostvars'][host]:
                variables.append(self.inventory['_meta']['hostvars'][host][variable])

        if len(list(set(variables))) == 1:
            return variables[0]

        return None

    def run_cmd_on_master(self, command, strip=True):
        """
            Run a command on the primary master and return the output
            command: string of the command to run on the primary master
            e.g: command = "echo 'hello world'"
        """

        command_output = subprocess.check_output(["/usr/bin/ossh", "root@" + self.primary_master, "-c", command])

        if strip:
            return command_output.strip()

        return command_output

    def convert_inv_to_os_name(self, hostname):
        """ convert ops hostname to the openshift hostname
            example: free-stg-master-03fb6 -> ip-172-31-78-254.us-east-2.compute.internal
        """

        if hostname not in self.inventory["_meta"]["hostvars"]:
            return None

        host_vars = self.inventory["_meta"]["hostvars"][hostname]

        if host_vars['oo_location'] == 'gcp':
            return hostname
        elif host_vars['oo_location'] == 'aws':
            return host_vars['ec2_private_dns_name']

    def convert_list_to_os_names(self, hostnames):
        """ convert a list of ops hostname to the openshift hostname
            example: ['free-stg-node-infra-a18ed', 'free-stg-node-compute-006ef'] ->
                     [u'ip-172-31-73-38.us-east-2.compute.internal',
                      u'ip-172-31-74-247.us-east-2.compute.internal']
        """

        if hostnames:
            converted_hosts = []

            for host in hostnames:
                os_host = self.convert_inv_to_os_name(host)
                converted_hosts.append(os_host)

            return converted_hosts

    def convert_os_to_inv_name(self, hostname):
        """ convert openshift name  to inventory name:
            example: 'ip-172-31-69-53.us-east-2.compute.internal' => free-stg-node-infra-70a4e
        """

        if hostname in self.cluster_nodes:
            return hostname

        for node in self.cluster_nodes:
            if hostname == self.inventory["_meta"]["hostvars"][node]["ec2_private_dns_name"]:
                return node

        return None
