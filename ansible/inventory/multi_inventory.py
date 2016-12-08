#!/usr/bin/env python2
'''
    Fetch and combine multiple inventory account settings into a single
    json hash.
'''
# vim: expandtab:tabstop=4:shiftwidth=4

from string import Template
from time import time
import argparse
import atexit
import copy
import errno
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import yaml

CONFIG_FILE_NAME = 'multi_inventory.yaml'
DEFAULT_CACHE_PATH = os.path.expanduser('~/.ansible/tmp/multi_inventory.cache')
FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))

class MultiInventoryAccount(object):
    """Object to represent an account"""
    def __init__(self, name, config, cache_path, cache_max_age=1800):
        self.name = name
        self.config = config
        self._inventory = None

        # set to global cache_max_age
        self.cache_max_age = cache_max_age
        # if an account setting exists, set to account cache_max_age
        if self.config.has_key('cache_max_age'):
            self.cache_max_age = self.config['cache_max_age']

        # set to global account cache_path
        self.cache_path = cache_path
        # if an account setting exists, set to account cache_path
        if self.config.has_key('cache_path'):
            self.cache_path = self.config['cache_path']

        # collect a list of clusters for this account
        self.clusters = []
        if self.config.has_key('cluster_vars') and \
            self.config['cluster_vars'].has_key('clusters'):
            self.clusters = self.config['cluster_vars']['clusters'].keys()

    @property
    def inventory(self):
        """property for inventory"""
        if self._inventory is None:
            self._inventory = MultiInventoryUtils.get_inventory_from_cache(os.path.join(self.cache_path, self.name))
            if self._inventory is None:
                self._inventory = {}
            else:
                self.apply_account_config()

        return self._inventory

    @inventory.setter
    def inventory(self, data):
        """setter for inventory"""
        self._inventory = data
        self.apply_account_config()

    @staticmethod
    def run_account_providers(accounts, force=False, validate_cache=True, account=None, debug=False):
        """Setup the provider call with proper variables and call the account's run_provider"""
        try:
            updated = False
            # if account parameter is present we only want refresh that specific account
            tmp_accounts = accounts
            if account:
                tmp_accounts = [acc for acc in accounts if acc.name == account]

            processes = {}
            for acc in tmp_accounts:
                if debug:
                    print "Calling run_provider for account: %s" % acc.name
                processes[acc.name] = acc.run_provider(force=force, validate_cache=validate_cache)

            # for each process collect stdout when its available
            for acc in tmp_accounts:
                if not processes[acc.name]['cached']:
                    proc = processes[acc.name]['proc']
                    out, err = proc.communicate()

                    # For any non-zero, raise an error on it
                    if proc.returncode != 0:
                        err_msg = 'Account: %s Error_Code: %s StdErr: [%s] Stdout: [%s]\n' % \
                                   (acc.name, proc.returncode, err.replace('\n', '\\n'), out.replace('\n', '\\n'))

                        #raise RuntimeError('\n'.join(err_msg))
                        sys.stderr.write(err_msg)
                    else:
                        updated = True
                        # The reason this exists here is that we
                        # are using the futures pattern.  The account object
                        # has run a subprocess and we are collecting the results.
                        data = json.loads(out)
                        acc.write_to_cache(data)
                        acc.inventory = data
        except ValueError as exc:
            print exc.message
            sys.exit(1)

        return updated

    def run_provider(self, force=False, validate_cache=False):
        """Setup the provider call with proper variables and call self.get_provider_tags

           force:  Whether to force an update on the account
           validate_cache:  Whether or not to validate the cache.
                         This happens in case of an account update

        """
        # force an update??
        if not force:
            # check if we want to validate the cache or if the cache is valid
            if not validate_cache or \
               MultiInventoryUtils.is_cache_valid(os.path.join(self.cache_path, self.name), self.cache_max_age):
                return {'cached': True, 'data': self.inventory}

        if self.config.has_key('provider_files'):
            tmp_dir = self.generate_config()

	# Update env vars after creating provider_config_files
	# so that we can grab the tmp_dir if it exists
        env = self.config.get('env_vars', {})
        if env and tmp_dir:
            for key, value in env.items():
                if value is None:
                    value = ''
                env[key] = Template(value).substitute(tmpdir=tmp_dir)

        if not env:
            env = os.environ

        provider = self.config['provider']
        # Allow relatively path'd providers in config file
        if os.path.isfile(os.path.join(FILE_PATH, self.config['provider'])):
            provider = os.path.join(FILE_PATH, self.config['provider'])

        # check to see if provider exists
        if not os.path.isfile(provider) or not os.access(provider, os.X_OK):
            raise RuntimeError("Problem with the provider.  Please check path " \
                        "and that it is executable. (%s)" % provider)

        cmds = [provider, '--list']

        if 'aws' in provider.lower():
            cmds.append('--refresh-cache')

        return {'cached': False,
                'proc': subprocess.Popen(cmds, stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=env)}

    def apply_cluster_vars(self):
        """Apply the account config cluster vars"""
        # cluster vars go here
        # do nothing for accounts that do not have cluster vars
        if not self.config.get('cluster_vars', None):
            return

        cluster_tag = self.config['cluster_vars']['cluster_tag']
        synthetic_hosts = self.config['cluster_vars'].get('synthetic_hosts', False)

        for cluster_name, cluster in self.config['cluster_vars']['clusters'].items():
            for host in self.inventory['_meta']['hostvars'].values():
                clusterid = MultiInventoryUtils.get_entry(host, cluster_tag)

                if clusterid == cluster_name:
                    MultiInventoryUtils.add_entry(host, 'oo_clusterid', clusterid)

                    for new_var, value in cluster.items():
                        MultiInventoryUtils.add_entry(host, new_var, value)

            # Apply synthetic host groups for boot strapping purposes
            if synthetic_hosts:
                synth_host = 'synthetic_%s' % cluster_name

                self.inventory['_meta']['hostvars'][synth_host] = {'oo_clusterid': cluster_name,
                                                                   'synthetic' : True}

                for new_var, value in cluster.items():
                    self.inventory['_meta']['hostvars'][synth_host][new_var] = value

                if not self.inventory.has_key('synthetic_hosts'):
                    self.inventory['synthetic_hosts'] = []

                self.inventory['synthetic_hosts'].append(synth_host)

    def apply_extra_vars(self):
        """Apply the account config extra vars """
        # Extra vars go here
        for new_var, value in self.config.get('extra_vars', {}).items():
            for data in self.inventory['_meta']['hostvars'].values():
                MultiInventoryUtils.add_entry(data, new_var, value)

    def apply_clone_vars(self):
        """Apply the account config clone vars """
        # Clone vars go here
        for to_name, from_name in self.config.get('clone_vars', {}).items():
            for data in self.inventory['_meta']['hostvars'].values():
                MultiInventoryUtils.add_entry(data, to_name, MultiInventoryUtils.get_entry(data, from_name))

    def apply_extra_groups(self):
        """Apply the account config for extra groups """
        for new_var, value in self.config.get('extra_groups', {}).items():
            for name, _ in self.inventory['_meta']['hostvars'].items():
                if 'synthetic_' in name:
                    continue

                self.inventory["%s_%s" % (new_var, value)] = copy.copy(self.inventory['all_hosts'])

    def apply_clone_groups(self):
        """Apply the account config for clone groups """
        for to_name, from_name in self.config.get('clone_groups', {}).items():
            for name, data in self.inventory['_meta']['hostvars'].items():
                if 'synthetic_' in name:
                    continue

                key = '%s_%s' % (to_name, MultiInventoryUtils.get_entry(data, from_name))
                if not self.inventory.has_key(key):
                    self.inventory[key] = []
                self.inventory[key].append(name)

    def apply_group_selectors(self):
        """Apply the account config for group selectors """
        # There could be multiple clusters per account.  We need to process these selectors
        # based upon the oo_clusterid_ variable.
        clusterids = [group for group in self.inventory if "oo_clusterid_" in group]

        for clusterid in clusterids:
            for selector in self.config.get('group_selectors', {}):
                if self.inventory.has_key(selector['from_group']):
                    hosts = list(set(self.inventory[clusterid]) & set(self.inventory[selector['from_group']]))
                    hosts.sort()

                    # Multiple clusters in an account
                    if self.inventory.has_key(selector['name']):
                        self.inventory[selector['name']].extend(hosts[0:selector['count']])
                    else:
                        self.inventory[selector['name']] = hosts[0:selector['count']]

                    for host in hosts:
                        if host in self.inventory[selector['name']]:
                            self.inventory['_meta']['hostvars'][host][selector['name']] = True
                        else:
                            self.inventory['_meta']['hostvars'][host][selector['name']] = False


    def apply_account_config(self):
        """ Apply account config settings """
        self.inventory['all_hosts'] = self.inventory['_meta']['hostvars'].keys()

        self.apply_cluster_vars()

        self.apply_extra_vars()

        self.apply_clone_vars()

        self.apply_extra_groups()

        self.apply_clone_groups()

        self.apply_group_selectors()

    def generate_config(self):
        """Generate the provider_files in a temporary directory"""
        prefix = 'multi_inventory.'
        tmp_dir_path = tempfile.mkdtemp(prefix=prefix)
        atexit.register(MultiInventoryUtils.cleanup, [tmp_dir_path])
        for provider_file in self.config['provider_files']:
            with open(os.path.join(tmp_dir_path, provider_file['name']), 'w+') as filedes:
                content = Template(provider_file['contents']).substitute(tmpdir=tmp_dir_path)
                filedes.write(content)

        return tmp_dir_path

    def write_to_cache(self, data):
        '''account cache writer'''
        MultiInventoryUtils.write_to_cache(os.path.join(self.cache_path, self.name), data)


class MultiInventoryException(Exception):
    '''Exceptions for MultiInventory class'''
    pass

# Need to figure out how to reduce the attributes.  Most are used for default settings
# and determining cache, cache_max_age, results, and storing account data
class MultiInventory(object):
    '''
       MultiInventory class:
            Opens a yaml config file and reads aws credentials.
            Stores a json hash of resources in result.
    '''

    def __init__(self, args=None):
        # Allow args to be passed when called as a library
        self.args = {}
        if args != None:
            self.args = args

        self.accounts = []
        self.cache_max_age = 1800
        self.cache_path = DEFAULT_CACHE_PATH
        self.config = None
        self.config_file = None

        # Store each individual restuls by account name in this variable
        self.all_inventory_results = {}

    def run(self):
        '''This method checks to see if the local cache is valid for the inventory.

           if the cache is valid; return cache
           else the credentials are loaded from multi_inventory.yaml or from the env
           and we attempt to get the inventory from the provider specified.
        '''
        # Finish loading configuration files
        self.load_config_settings()

        results = {}

        # --refresh
        # Either force a refresh on the cache or validate it
        if self.args.get('refresh_cache', None):
            results = self.get_inventory()
        #--from-cache was called.
        elif self.args.get('from_cache', False):
            results = MultiInventoryUtils.get_inventory_from_cache(self.cache_path)
        #--list was called.
        elif not MultiInventoryUtils.is_cache_valid(self.cache_path, self.cache_max_age):
            results = self.get_inventory()
        else:
            # get data from disk
            results = MultiInventoryUtils.get_inventory_from_cache(self.cache_path)

        return results

    def load_config_settings(self):
        """Setup the config settings for cache, config file, etc"""

        # Prefer a file in the same directory, fall back to a file in etc
        if os.path.isfile(os.path.join(FILE_PATH, CONFIG_FILE_NAME)):
            self.config_file = os.path.join(FILE_PATH, CONFIG_FILE_NAME)
        elif os.path.isfile(os.path.join(os.path.sep, 'etc', 'ansible', CONFIG_FILE_NAME)):
            self.config_file = os.path.join(os.path.sep, 'etc', 'ansible', CONFIG_FILE_NAME)
        else:
            self.config_file = None # expect env vars

        # load yaml
        if self.config_file and os.path.isfile(self.config_file):
            self.config = self.load_yaml_config()
            self.cache_max_age = self.config['cache_max_age']
        elif os.environ.has_key("AWS_ACCESS_KEY_ID") and os.environ.has_key("AWS_SECRET_ACCESS_KEY"):
            # Build a default config
            self.config = {}
            # pylint: disable=line-too-long
            self.config['accounts'] = {'default': {'cache_location': DEFAULT_CACHE_PATH,
                                                   'provider': 'aws/hosts/ec2.py',
                                                   'env_vars': {'AWS_ACCESS_KEY_ID':     os.environ["AWS_ACCESS_KEY_ID"],
                                                                'AWS_SECRET_ACCESS_KEY': os.environ["AWS_SECRET_ACCESS_KEY"],
                                                               }
                                                  }
                                      }

            self.cache_max_age = 300
        else:
            raise RuntimeError("Could not find valid ec2 credentials in the environment.")

        if self.config.has_key('cache_location'):
            self.cache_path = self.config['cache_location']


    def load_yaml_config(self, conf_file=None):
        """Load a yaml config file with credentials to query the respective cloud for inventory"""
        config = None

        if not conf_file:
            conf_file = self.config_file

        with open(conf_file) as conf:
            config = yaml.safe_load(conf)

        return config


    def build_accounts(self):
        '''create an account array and return it'''
        self.accounts = []
        account_names = []
        for acc_name, account in self.config['accounts'].items():
            if acc_name in account_names:
                raise MultiInventoryException('Multiple accounts exist with the same name. ' \
                                              'This is not permitted. name=[%s]' % acc_name)

            account_names.append(acc_name)

            self.accounts.append(MultiInventoryAccount(acc_name,
                                                       account,
                                                       self.config['cache_account_location'],
                                                       self.config['cache_max_age']))

    def get_account_from_cluster(self, cluster):
        '''return the account if it has the specified cluster'''
        for account in self.accounts:
            if cluster in account.clusters:
                return account.name

        raise MultiInventoryException('Cluster [%s] does not exist. Exiting.' % cluster)

    def get_inventory(self):
        """Create the subprocess to fetch tags from a provider.
        Query all of the different accounts for their tags.  Once completed
        store all of their results into one merged updated hash.
        """
        # instantiate all the accounts
        self.build_accounts()

        # Determine if an account was passed from the cli or args
        account = None
        if self.args.get('account', None):
            account = self.args['account']

            # Validate the account exists
            if account not in [acc.name for acc in self.accounts]:
                raise MultiInventoryException('Account [%s] does not exist. Exiting.' % account)

        # find the specified account by cluster
        elif self.args.get('cluster', None):
            account = self.get_account_from_cluster(self.args['cluster'])

        # Run the account providers.  If account is set, only update the desired account
        updated = MultiInventoryAccount.run_account_providers(self.accounts,
                                                              force=self.args.get('refresh_cache', False),
                                                              validate_cache=self.args.get('list', True),
                                                              account=account,
                                                              debug=self.args.get('debug', False))

        all_results = {}
        #values = self.accounts[0].inventory.values()
        #values.insert(0, all_results)
        for account in self.accounts:
            # Build results by merging all dictionaries
            MultiInventoryUtils.merge_destructively(all_results, account.inventory)

        # only write cache if something was updated
        # in the run_account_provider.
        if updated:
            MultiInventoryUtils.write_to_cache(self.cache_path, all_results)

        return all_results


    def parse_cli_args(self):
        """ Command line argument processing """

        parser = argparse.ArgumentParser(
            description='Produce an Ansible Inventory file based on a provider')
        parser.add_argument('--refresh-cache', action='store_true', default=False,
                            help='Fetch cached only instances (default: False)')
        parser.add_argument('--list', action='store_true', default=True,
                            help='List instances (default: True)')
        parser.add_argument('--cluster', action='store', default=False,
                            help='Refresh an account by cluster name')
        parser.add_argument('--account', action='store', default=False,
                            help='Refresh an account')
        parser.add_argument('--debug', action='store_true', default=False,
                            help='Whether to print debug')
        parser.add_argument('--from-cache', action='store_true', default=False,
                            help='Whether to pull from cache')
        self.args = parser.parse_args().__dict__

class MultiInventoryUtils(object):
    """place for shared utilities"""
    @staticmethod
    def write_to_cache(cache_path, data):
        """Writes data in JSON format to cache_path"""

        # if it does not exist, try and create it.
        if not os.path.isfile(cache_path):
            path = os.path.dirname(cache_path)
            try:
                os.makedirs(path)
            except OSError as exc:
                if exc.errno != errno.EEXIST or not os.path.isdir(path):
                    raise

        json_data = MultiInventoryUtils.json_format_dict(data, True)
        with open(cache_path, 'w') as cache:
            try:
                fcntl.flock(cache, fcntl.LOCK_EX)
                cache.write(json_data)
            finally:
                fcntl.flock(cache, fcntl.LOCK_UN)

    @staticmethod
    def json_format_dict(data, pretty=False):
        """ Converts a dict to a JSON object and dumps it as a formatted string """

        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
        else:
            return json.dumps(data)

    @staticmethod
    def get_inventory_from_cache(cache_path):
        """Reads the inventory from the cache file and returns it as a JSON object"""
        results = None
        if not os.path.isfile(cache_path):
            return results

        with open(cache_path, 'r') as cache:
            results = json.loads(cache.read())

        return results

    @staticmethod
    def is_cache_valid(cache_path, age=1800):
        """ Determines if the cache files have expired, or if it is still valid """

        if os.path.isfile(cache_path):
            mod_time = os.path.getmtime(cache_path)
            current_time = time()
            if (mod_time + age) > current_time:
                return True

        return False

    @staticmethod
    def cleanup(files):
        """Clean up on exit """
        for sfile in files:
            if os.path.exists(sfile):
                if os.path.isdir(sfile):
                    shutil.rmtree(sfile)
                elif os.path.isfile(sfile):
                    os.remove(sfile)

    @staticmethod
    def merge_destructively(input_a, input_b):
        """merges input_b into input_a"""
        for key in input_b:
            if key in input_a:
                if isinstance(input_a[key], dict) and isinstance(input_b[key], dict):
                    MultiInventoryUtils.merge_destructively(input_a[key], input_b[key])
                elif input_a[key] == input_b[key]:
                    pass # same leaf value
                # both lists so add each element in b to a if it does ! exist
                elif isinstance(input_a[key], list) and isinstance(input_b[key], list):
                    for result in input_b[key]:
                        if result not in input_a[key]:
                            input_a[key].append(result)
                # a is a list and not b
                elif isinstance(input_a[key], list):
                    if input_b[key] not in input_a[key]:
                        input_a[key].append(input_b[key])
                elif isinstance(input_b[key], list):
                    input_a[key] = [input_a[key]] + [k for k in input_b[key] if k != input_a[key]]
                else:
                    input_a[key] = [input_a[key], input_b[key]]
            else:
                input_a[key] = input_b[key]
        return input_a

    @staticmethod
    def add_entry(data, keys, item):
        """Add an item to a dictionary with key notation a.b.c
           d = {'a': {'b': 'c'}}}
           keys = a.b
           item = c
        """
        if "." in keys:
            key, rest = keys.split(".", 1)
            if key not in data:
                data[key] = {}
            MultiInventoryUtils.add_entry(data[key], rest, item)
        else:
            data[keys] = item

    @staticmethod
    def get_entry(data, keys):
        """ Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            keys = a.b
            return c
        """
        if keys and "." in keys:
            key, rest = keys.split(".", 1)
            if data.has_key(key):
                return MultiInventoryUtils.get_entry(data[key], rest)

            return None
        else:
            return data.get(keys, None)


if __name__ == "__main__":
    MI2 = MultiInventory()
    MI2.parse_cli_args()
    print MultiInventoryUtils.json_format_dict(MI2.run(), True)
