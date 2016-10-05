#!/usr/bin/env python # pylint: disable=too-many-lines
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|
'''
   OpenShiftCLI class that wraps the oc commands in a subprocess
'''
# pylint: disable=too-many-lines

import atexit
import copy
import json
import os
import re
import shutil
import subprocess
import yaml

# This is here because of a bug that causes yaml
# to incorrectly handle timezone info on timestamps
def timestamp_constructor(_, node):
    '''return timestamps as strings'''
    return str(node.value)
yaml.add_constructor(u'tag:yaml.org,2002:timestamp', timestamp_constructor)

class OpenShiftCLIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class OpenShiftCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self,
                 namespace,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftCLI '''
        self.namespace = namespace
        self.verbose = verbose
        self.kubeconfig = kubeconfig

    # Pylint allows only 5 arguments to be passed.
    # pylint: disable=too-many-arguments
    def _replace_content(self, resource, rname, content, force=False):
        ''' replace the current object with the content '''
        res = self._get(resource, rname)
        if not res['results']:
            return res

        fname = '/tmp/%s' % rname
        yed = Yedit(fname, res['results'][0])
        changes = []
        for key, value in content.items():
            changes.append(yed.put(key, value))

        if any([change[0] for change in changes]):
            yed.write()

            atexit.register(Utils.cleanup, [fname])

            return self._replace(fname, force)

        return {'returncode': 0, 'updated': False}

    def _replace(self, fname, force=False):
        '''return all pods '''
        cmd = ['-n', self.namespace, 'replace', '-f', fname]
        if force:
            cmd.append('--force')
        return self.openshift_cmd(cmd)

    def _create_from_content(self, rname, content):
        '''return all pods '''
        fname = '/tmp/%s' % rname
        yed = Yedit(fname, content=content)
        yed.write()

        atexit.register(Utils.cleanup, [fname])

        return self._create(fname)

    def _create(self, fname):
        '''return all pods '''
        return self.openshift_cmd(['create', '-f', fname, '-n', self.namespace])

    def _delete(self, resource, rname, selector=None):
        '''return all pods '''
        cmd = ['delete', resource, rname, '-n', self.namespace]
        if selector:
            cmd.append('--selector=%s' % selector)

        return self.openshift_cmd(cmd)

    def _process(self, template_name, create=False, params=None):
        '''return all pods '''
        cmd = ['process', template_name, '-n', self.namespace]
        if params:
            param_str = ["%s=%s" % (key, value) for key, value in params.items()]
            cmd.append('-v')
            cmd.extend(param_str)

        results = self.openshift_cmd(cmd, output=True)

        if results['returncode'] != 0 or not create:
            return results

        fname = '/tmp/%s' % template_name
        yed = Yedit(fname, results['results'])
        yed.write()

        atexit.register(Utils.cleanup, [fname])

        return self.openshift_cmd(['-n', self.namespace, 'create', '-f', fname])

    def _get(self, resource, rname=None, selector=None):
        '''return a resource by name '''
        cmd = ['get', resource]
        if selector:
            cmd.append('--selector=%s' % selector)
        if self.namespace:
            cmd.extend(['-n', self.namespace])

        cmd.extend(['-o', 'json'])

        if rname:
            cmd.append(rname)

        rval = self.openshift_cmd(cmd, output=True)

        # Ensure results are retuned in an array
        if rval.has_key('items'):
            rval['results'] = rval['items']
        elif not isinstance(rval['results'], list):
            rval['results'] = [rval['results']]

        return rval

    def _schedulable(self, node=None, selector=None, schedulable=True):
        ''' perform oadm manage-node scheduable '''
        cmd = ['manage-node']
        if node:
            cmd.extend(node)
        else:
            cmd.append('--selector=%s' % selector)

        cmd.append('--schedulable=%s' % schedulable)

        return self.openshift_cmd(cmd, oadm=True, output=True, output_type='raw')

    def _list_pods(self, node=None, selector=None, pod_selector=None):
        ''' perform oadm manage-node evacuate '''
        cmd = ['manage-node']
        if node:
            cmd.extend(node)
        else:
            cmd.append('--selector=%s' % selector)

        if pod_selector:
            cmd.append('--pod-selector=%s' % pod_selector)

        cmd.extend(['--list-pods', '-o', 'json'])

        return self.openshift_cmd(cmd, oadm=True, output=True, output_type='raw')

    #pylint: disable=too-many-arguments
    def _evacuate(self, node=None, selector=None, pod_selector=None, dry_run=False, grace_period=None):
        ''' perform oadm manage-node evacuate '''
        cmd = ['manage-node']
        if node:
            cmd.extend(node)
        else:
            cmd.append('--selector=%s' % selector)

        if dry_run:
            cmd.append('--dry-run')

        if pod_selector:
            cmd.append('--pod-selector=%s' % pod_selector)

        if grace_period:
            cmd.append('--grace-period=%s' % int(grace_period))

        cmd.append('--evacuate')

        return self.openshift_cmd(cmd, oadm=True, output=True, output_type='raw')

    def openshift_cmd(self, cmd, oadm=False, output=False, output_type='json'):
        '''Base command for oc '''
        cmds = []
        if oadm:
            cmds = ['/usr/bin/oadm']
        else:
            cmds = ['/usr/bin/oc']

        cmds.extend(cmd)

        rval = {}
        results = ''
        err = None

        if self.verbose:
            print ' '.join(cmds)

        proc = subprocess.Popen(cmds,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env={'KUBECONFIG': self.kubeconfig})

        stdout, stderr = proc.communicate()
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

class Utils(object):
    ''' utilities for openshiftcli modules '''
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
    def create_files_from_contents(content, content_type=None):
        '''Turn an array of dict: filename, content into a files array'''
        if not isinstance(content, list):
            content = [content]
        files = []
        for item in content:
            path = Utils.create_file(item['path'], item['data'], ftype=content_type)
            files.append({'name': os.path.basename(path), 'path': path})
        return files

    @staticmethod
    def cleanup(files):
        '''Clean up on exit '''
        for sfile in files:
            if os.path.exists(sfile):
                if os.path.isdir(sfile):
                    shutil.rmtree(sfile)
                elif os.path.isfile(sfile):
                    os.remove(sfile)


    @staticmethod
    def exists(results, _name):
        ''' Check to see if the results include the name '''
        if not results:
            return False


        if Utils.find_result(results, _name):
            return True

        return False

    @staticmethod
    def find_result(results, _name):
        ''' Find the specified result by name'''
        rval = None
        for result in results:
            if result.has_key('metadata') and result['metadata']['name'] == _name:
                rval = result
                break

        return rval

    @staticmethod
    def get_resource_file(sfile, sfile_type='yaml'):
        ''' return the service file  '''
        contents = None
        with open(sfile) as sfd:
            contents = sfd.read()

        if sfile_type == 'yaml':
            contents = yaml.safe_load(contents)
        elif sfile_type == 'json':
            contents = json.loads(contents)

        return contents

    # Disabling too-many-branches.  This is a yaml dictionary comparison function
    # pylint: disable=too-many-branches,too-many-return-statements,too-many-statements
    @staticmethod
    def check_def_equal(user_def, result_def, skip_keys=None, debug=False):
        ''' Given a user defined definition, compare it with the results given back by our query.  '''

        # Currently these values are autogenerated and we do not need to check them
        skip = ['metadata', 'status']
        if skip_keys:
            skip.extend(skip_keys)

        for key, value in result_def.items():
            if key in skip:
                continue

            # Both are lists
            if isinstance(value, list):
                if not user_def.has_key(key):
                    if debug:
                        print 'User data does not have key [%s]' % key
                        print 'User data: %s' % user_def
                    return False

                if not isinstance(user_def[key], list):
                    if debug:
                        print 'user_def[key] is not a list'
                    return False

                if len(user_def[key]) != len(value):
                    if debug:
                        print "List lengths are not equal."
                        print "key=[%s]: user_def[%s] != value[%s]" % (key, len(user_def[key]), len(value))
                        print "user_def: %s" % user_def[key]
                        print "value: %s" % value
                    return False


                for values in zip(user_def[key], value):
                    if isinstance(values[0], dict) and isinstance(values[1], dict):
                        if debug:
                            print 'sending list - list'
                            print type(values[0])
                            print type(values[1])
                        result = Utils.check_def_equal(values[0], values[1], skip_keys=skip_keys, debug=debug)
                        if not result:
                            print 'list compare returned false'
                            return False

                    elif value != user_def[key]:
                        if debug:
                            print 'value should be identical'
                            print value
                            print user_def[key]
                        return False

            # recurse on a dictionary
            elif isinstance(value, dict):
                if not user_def.has_key(key):
                    if debug:
                        print "user_def does not have key [%s]" % key
                    return False
                if not isinstance(user_def[key], dict):
                    if debug:
                        print "dict returned false: not instance of dict"
                    return False

                # before passing ensure keys match
                api_values = set(value.keys()) - set(skip)
                user_values = set(user_def[key].keys()) - set(skip)
                if api_values != user_values:
                    if debug:
                        print "keys are not equal in dict"
                        print api_values
                        print user_values
                    return False

                result = Utils.check_def_equal(user_def[key], value, skip_keys=skip_keys, debug=debug)
                if not result:
                    if debug:
                        print "dict returned false"
                        print result
                    return False

            # Verify each key, value pair is the same
            else:
                if not user_def.has_key(key) or value != user_def[key]:
                    if debug:
                        print "value not equal; user_def does not have key"
                        print key
                        print value
                        print user_def[key]
                    return False

        return True

class OpenShiftCLIConfig(object):
    '''Generic Config'''
    def __init__(self, rname, namespace, kubeconfig, options):
        self.kubeconfig = kubeconfig
        self.name = rname
        self.namespace = namespace
        self._options = options

    @property
    def config_options(self):
        ''' return config options '''
        return self._options

    def to_option_list(self):
        '''return all options as a string'''
        return self.stringify()

    def stringify(self):
        ''' return the options hash as cli params in a string '''
        rval = []
        for key, data in self.config_options.items():
            if data['include'] and data['value']:
                rval.append('--%s=%s' % (key.replace('_', '-'), data['value']))

        return rval

class YeditException(Exception):
    ''' Exception class for Yedit '''
    pass

class Yedit(object):
    ''' Class to modify yaml files '''
    re_valid_key = r"(((\[-?\d+\])|([0-9a-zA-Z%s/_-]+)).?)+$"
    re_key = r"(?:\[(-?\d+)\])|([0-9a-zA-Z%s/_-]+)"
    com_sep = set(['.', '#', '|', ':'])

    # pylint: disable=too-many-arguments
    def __init__(self, filename=None, content=None, content_type='yaml', separator='.', backup=False):
        self.content = content
        self._separator = separator
        self.filename = filename
        self.__yaml_dict = content
        self.content_type = content_type
        self.backup = backup
        self.load(content_type=self.content_type)
        if self.__yaml_dict == None:
            self.__yaml_dict = {}

    @property
    def separator(self):
        ''' getter method for yaml_dict '''
        return self._separator

    @separator.setter
    def separator(self):
        ''' getter method for yaml_dict '''
        return self._separator

    @property
    def yaml_dict(self):
        ''' getter method for yaml_dict '''
        return self.__yaml_dict

    @yaml_dict.setter
    def yaml_dict(self, value):
        ''' setter method for yaml_dict '''
        self.__yaml_dict = value

    @staticmethod
    def parse_key(key, sep='.'):
        '''parse the key allowing the appropriate separator'''
        common_separators = list(Yedit.com_sep - set([sep]))
        return re.findall(Yedit.re_key % ''.join(common_separators), key)

    @staticmethod
    def valid_key(key, sep='.'):
        '''validate the incoming key'''
        common_separators = list(Yedit.com_sep - set([sep]))
        if not re.match(Yedit.re_valid_key % ''.join(common_separators), key):
            return False

        return True

    @staticmethod
    def remove_entry(data, key, sep='.'):
        ''' remove data at location key '''
        if key == '' and isinstance(data, dict):
            data.clear()
            return True
        elif key == '' and isinstance(data, list):
            del data[:]
            return True

        if not (key and Yedit.valid_key(key, sep)) and isinstance(data, (list, dict)):
            return None

        key_indexes = Yedit.parse_key(key, sep)
        for arr_ind, dict_key in key_indexes[:-1]:
            if dict_key and isinstance(data, dict):
                data = data.get(dict_key, None)
            elif arr_ind and isinstance(data, list) and int(arr_ind) <= len(data) - 1:
                data = data[int(arr_ind)]
            else:
                return None

        # process last index for remove
        # expected list entry
        if key_indexes[-1][0]:
            if isinstance(data, list) and int(key_indexes[-1][0]) <= len(data) - 1:
                del data[int(key_indexes[-1][0])]
                return True

        # expected dict entry
        elif key_indexes[-1][1]:
            if isinstance(data, dict):
                del data[key_indexes[-1][1]]
                return True

    @staticmethod
    def add_entry(data, key, item=None, sep='.'):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            key = a#b
            return c
        '''
        if key == '':
            pass
        elif not (key and Yedit.valid_key(key, sep)) and isinstance(data, (list, dict)):
            return None

        key_indexes = Yedit.parse_key(key, sep)
        for arr_ind, dict_key in key_indexes[:-1]:
            if dict_key:
                if isinstance(data, dict) and data.has_key(dict_key) and data[dict_key]:
                    data = data[dict_key]
                    continue

                elif data and not isinstance(data, dict):
                    return None

                data[dict_key] = {}
                data = data[dict_key]

            elif arr_ind and isinstance(data, list) and int(arr_ind) <= len(data) - 1:
                data = data[int(arr_ind)]
            else:
                return None

        if key == '':
            data = item

        # process last index for add
        # expected list entry
        elif key_indexes[-1][0] and isinstance(data, list) and int(key_indexes[-1][0]) <= len(data) - 1:
            data[int(key_indexes[-1][0])] = item

        # expected dict entry
        elif key_indexes[-1][1] and isinstance(data, dict):
            data[key_indexes[-1][1]] = item

        return data

    @staticmethod
    def get_entry(data, key, sep='.'):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            key = a.b
            return c
        '''
        if key == '':
            pass
        elif not (key and Yedit.valid_key(key, sep)) and isinstance(data, (list, dict)):
            return None

        key_indexes = Yedit.parse_key(key, sep)
        for arr_ind, dict_key in key_indexes:
            if dict_key and isinstance(data, dict):
                data = data.get(dict_key, None)
            elif arr_ind and isinstance(data, list) and int(arr_ind) <= len(data) - 1:
                data = data[int(arr_ind)]
            else:
                return None

        return data

    def write(self):
        ''' write to file '''
        if not self.filename:
            raise YeditException('Please specify a filename.')

        if self.backup and self.file_exists():
            shutil.copy(self.filename, self.filename + '.orig')

        tmp_filename = self.filename + '.yedit'
        try:
            with open(tmp_filename, 'w') as yfd:
                yml_dump = yaml.safe_dump(self.yaml_dict, default_flow_style=False)
                for line in yml_dump.strip().split('\n'):
                    if '{{' in line and '}}' in line:
                        yfd.write(line.replace("'{{", '"{{').replace("}}'", '}}"') + '\n')
                    else:
                        yfd.write(line + '\n')
        except Exception as err:
            raise YeditException(err.message)

        os.rename(tmp_filename, self.filename)

        return (True, self.yaml_dict)

    def read(self):
        ''' read from file '''
        # check if it exists
        if self.filename == None or not self.file_exists():
            return None

        contents = None
        with open(self.filename) as yfd:
            contents = yfd.read()

        return contents

    def file_exists(self):
        ''' return whether file exists '''
        if os.path.exists(self.filename):
            return True

        return False

    def load(self, content_type='yaml'):
        ''' return yaml file '''
        contents = self.read()

        if not contents and not self.content:
            return None

        if self.content:
            if isinstance(self.content, dict):
                self.yaml_dict = self.content
                return self.yaml_dict
            elif isinstance(self.content, str):
                contents = self.content

        # check if it is yaml
        try:
            if content_type == 'yaml' and contents:
                self.yaml_dict = yaml.load(contents)
            elif content_type == 'json' and contents:
                self.yaml_dict = json.loads(contents)
        except yaml.YAMLError as err:
            # Error loading yaml or json
            YeditException('Problem with loading yaml file. %s' % err)

        return self.yaml_dict

    def get(self, key):
        ''' get a specified key'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, key, self.separator)
        except KeyError as _:
            entry = None

        return entry

    def pop(self, path, key_or_item):
        ''' remove a key, value pair from a dict or an item for a list'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path, self.separator)
        except KeyError as _:
            entry = None

        if entry == None:
            return  (False, self.yaml_dict)

        if isinstance(entry, dict):
            # pylint: disable=no-member,maybe-no-member
            if entry.has_key(key_or_item):
                entry.pop(key_or_item)
                return (True, self.yaml_dict)
            return (False, self.yaml_dict)

        elif isinstance(entry, list):
            # pylint: disable=no-member,maybe-no-member
            ind = None
            try:
                ind = entry.index(key_or_item)
            except ValueError:
                return (False, self.yaml_dict)

            entry.pop(ind)
            return (True, self.yaml_dict)

        return (False, self.yaml_dict)


    def delete(self, path):
        ''' remove path from a dict'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path, self.separator)
        except KeyError as _:
            entry = None

        if entry == None:
            return  (False, self.yaml_dict)

        result = Yedit.remove_entry(self.yaml_dict, path, self.separator)
        if not result:
            return (False, self.yaml_dict)

        return (True, self.yaml_dict)

    def exists(self, path, value):
        ''' check if value exists at path'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path, self.separator)
        except KeyError as _:
            entry = None

        if isinstance(entry, list):
            if value in entry:
                return True
            return False

        elif isinstance(entry, dict):
            if isinstance(value, dict):
                rval = False
                for key, val  in value.items():
                    if  entry[key] != val:
                        rval = False
                        break
                else:
                    rval = True
                return rval

            return value in entry

        return entry == value

    def append(self, path, value):
        '''append value to a list'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path, self.separator)
        except KeyError as _:
            entry = None

        if entry == None or not isinstance(entry, list):
            return (False, self.yaml_dict)

        # pylint: disable=no-member,maybe-no-member
        entry.append(value)
        return (True, self.yaml_dict)

    # pylint: disable=too-many-arguments
    def update(self, path, value, index=None, curr_value=None):
        ''' put path, value into a dict '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path, self.separator)
        except KeyError as _:
            entry = None

        if isinstance(entry, dict):
            # pylint: disable=no-member,maybe-no-member
            if not isinstance(value, dict):
                raise YeditException('Cannot replace key, value entry in dict with non-dict type.' \
                                     ' value=[%s]  [%s]' % (value, type(value)))

            entry.update(value)
            return (True, self.yaml_dict)

        elif isinstance(entry, list):
            # pylint: disable=no-member,maybe-no-member
            ind = None
            if curr_value:
                try:
                    ind = entry.index(curr_value)
                except ValueError:
                    return (False, self.yaml_dict)

            elif index != None:
                ind = index

            if ind != None and entry[ind] != value:
                entry[ind] = value
                return (True, self.yaml_dict)

            # see if it exists in the list
            try:
                ind = entry.index(value)
            except ValueError:
                # doesn't exist, append it
                entry.append(value)
                return (True, self.yaml_dict)

            #already exists, return
            if ind != None:
                return (False, self.yaml_dict)
        return (False, self.yaml_dict)

    def put(self, path, value):
        ''' put path, value into a dict '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path, self.separator)
        except KeyError as _:
            entry = None

        if entry == value:
            return (False, self.yaml_dict)

        tmp_copy = copy.deepcopy(self.yaml_dict)
        result = Yedit.add_entry(tmp_copy, path, value, self.separator)
        if not result:
            return (False, self.yaml_dict)

        self.yaml_dict = tmp_copy

        return (True, self.yaml_dict)

    def create(self, path, value):
        ''' create a yaml file '''
        if not self.file_exists():
            tmp_copy = copy.deepcopy(self.yaml_dict)
            result = Yedit.add_entry(tmp_copy, path, value, self.separator)
            if result:
                self.yaml_dict = tmp_copy
                return (True, self.yaml_dict)

        return (False, self.yaml_dict)

# pylint: disable=too-many-instance-attributes
class RoleConfig(object):
    ''' Handle route options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 kubeconfig,
                 kind='Role',
                 rules=None):
        ''' constructor for handling route options '''
        self.kubeconfig = kubeconfig
        self.kind = kind
        self.name = sname
        self.namespace = namespace
        self.rules = rules
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a service as a dict '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = self.kind
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        self.data['rules'] = self.rules or []

# pylint: disable=too-many-instance-attributes
class Role(Yedit):
    ''' Class to wrap the oc command line tools '''
    rule_path = "rules"

    def __init__(self, content, kind='Role'):
        '''Role constructor'''
        super(Role, self).__init__(content=content)
        self.kind = kind

    def get_rules(self):
        ''' return cert '''
        return self.get(Role.rule_path) or []


class ClusterRole(Role):
    ''' Class to wrap the oc command line tools '''
    rule_path = "rules"

    def __init__(self, content, kind='ClusterRole'):
        '''ClusterRole constructor'''
        super(ClusterRole, self).__init__(content=content)
        self.kind = kind

    def get_rules(self):
        ''' return cert '''
        return self.get(Role.rule_path) or []

# pylint: disable=too-many-instance-attributes
class RoleBindingConfig(object):
    ''' Handle route options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 kubeconfig,
                 group_names=None,
                 role_ref=None,
                 subjects=None,
                 usernames=None):
        ''' constructor for handling route options '''
        self.kubeconfig = kubeconfig
        self.name = sname
        self.namespace = namespace
        self.group_names = group_names
        self.role_ref = role_ref
        self.subjects = subjects
        self.usernames = usernames
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a service as a dict '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = 'RoleBinding'
        self.data['groupNames'] = self.group_names
        self.data['metadata']['name'] = self.name
        self.data['metadata']['namespace'] = self.namespace

        self.data['roleRef'] = self.role_ref
        self.data['subjects'] = self.subjects
        self.data['userNames'] = self.usernames


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class RoleBinding(Yedit):
    ''' Class to wrap the oc command line tools '''
    group_names_path = "groupNames"
    role_ref_path = "roleRef"
    subjects_path = "subjects"
    user_names_path = "userNames"

    kind = 'RoleBinding'

    def __init__(self, content):
        '''RoleBinding constructor'''
        super(RoleBinding, self).__init__(content=content)
        self._subjects = None
        self._role_ref = None
        self._group_names = None
        self._user_names = None

    @property
    def subjects(self):
        ''' subjects property '''
        if self._subjects == None:
            self._subjects = self.get_subjects()
        return self._subjects

    @subjects.setter
    def subjects(self, data):
        ''' subjects property setter'''
        self._subjects = data

    @property
    def role_ref(self):
        ''' role_ref property '''
        if self._role_ref == None:
            self._role_ref = self.get_role_ref()
        return self._role_ref

    @role_ref.setter
    def role_ref(self, data):
        ''' role_ref property setter'''
        self._role_ref = data

    @property
    def group_names(self):
        ''' group_names property '''
        if self._group_names == None:
            self._group_names = self.get_group_names()
        return self._group_names

    @group_names.setter
    def group_names(self, data):
        ''' group_names property setter'''
        self._group_names = data

    @property
    def user_names(self):
        ''' user_names property '''
        if self._user_names == None:
            self._user_names = self.get_user_names()
        return self._user_names

    @user_names.setter
    def user_names(self, data):
        ''' user_names property setter'''
        self._user_names = data

    def get_group_names(self):
        ''' return groupNames '''
        return self.get(RoleBinding.group_names_path) or []

    def get_user_names(self):
        ''' return usernames '''
        return self.get(RoleBinding.user_names_path) or []

    def get_role_ref(self):
        ''' return role_ref '''
        return self.get(RoleBinding.role_ref_path) or {}

    def get_subjects(self):
        ''' return subjects '''
        return self.get(RoleBinding.subjects_path) or []

    #### ADD #####
    def add_subject(self, inc_subject):
        ''' add a subject '''
        if self.subjects:
            self.subjects.append(inc_subject)
        else:
            self.put(RoleBinding.subjects_path, [inc_subject])

        return True

    def add_role_ref(self, inc_role_ref):
        ''' add a role_ref '''
        if not self.role_ref:
            self.put(RoleBinding.role_ref_path, {"name": inc_role_ref})
            return True

        return False

    def add_group_names(self, inc_group_names):
        ''' add a group_names '''
        if self.group_names:
            self.group_names.append(inc_group_names)
        else:
            self.put(RoleBinding.group_names_path, [inc_group_names])

        return True

    def add_user_name(self, inc_user_name):
        ''' add a username '''
        if self.user_names:
            self.user_names.append(inc_user_name)
        else:
            self.put(RoleBinding.user_names_path, [inc_user_name])

        return True

    #### /ADD #####

    #### Remove #####
    def remove_subject(self, inc_subject):
        ''' remove a subject '''
        try:
            self.subjects.remove(inc_subject)
        except ValueError as _:
            return False

        return True

    def remove_role_ref(self, inc_role_ref):
        ''' remove a role_ref '''
        if self.role_ref and self.role_ref['name'] == inc_role_ref:
            del self.role_ref['name']
            return True

        return False

    def remove_group_name(self, inc_group_name):
        ''' remove a groupname '''
        try:
            self.group_names.remove(inc_group_name)
        except ValueError as _:
            return False

        return True

    def remove_user_name(self, inc_user_name):
        ''' remove a username '''
        try:
            self.user_names.remove(inc_user_name)
        except ValueError as _:
            return False

        return True

    #### /REMOVE #####

    #### UPDATE #####
    def update_subject(self, inc_subject):
        ''' update a subject '''
        try:
            index = self.subjects.index(inc_subject)
        except ValueError as _:
            return self.add_subject(inc_subject)

        self.subjects[index] = inc_subject

        return True

    def update_group_name(self, inc_group_name):
        ''' update a groupname '''
        try:
            index = self.group_names.index(inc_group_name)
        except ValueError as _:
            return self.add_group_names(inc_group_name)

        self.group_names[index] = inc_group_name

        return True

    def update_user_name(self, inc_user_name):
        ''' update a username '''
        try:
            index = self.user_names.index(inc_user_name)
        except ValueError as _:
            return self.add_user_name(inc_user_name)

        self.user_names[index] = inc_user_name

        return True

    def update_role_ref(self, inc_role_ref):
        ''' update a role_ref '''
        self.role_ref['name'] = inc_role_ref

        return True

    #### /UPDATE #####

    #### FIND ####
    def find_subject(self, inc_subject):
        ''' find a subject '''
        index = None
        try:
            index = self.subjects.index(inc_subject)
        except ValueError as _:
            return index

        return index

    def find_group_name(self, inc_group_name):
        ''' find a group_name '''
        index = None
        try:
            index = self.group_names.index(inc_group_name)
        except ValueError as _:
            return index

        return index

    def find_user_name(self, inc_user_name):
        ''' find a user_name '''
        index = None
        try:
            index = self.user_names.index(inc_user_name)
        except ValueError as _:
            return index

        return index

    def find_role_ref(self, inc_role_ref):
        ''' find a user_name '''
        if self.role_ref and self.role_ref['name'] == inc_role_ref['name']:
            return self.role_ref

        return None

# pylint: disable=too-many-instance-attributes
class SecurityContextConstraintsConfig(object):
    ''' Handle route options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 kubeconfig,
                 options=None,
                 fs_group='MustRunAs',
                 default_add_capabilities=None,
                 groups=None,
                 priority=None,
                 required_drop_capabilities=None,
                 run_as_user='MustRunAsRange',
                 se_linux_context='MustRunAs',
                 supplemental_groups='RunAsAny',
                 users=None,
                 annotations=None):
        ''' constructor for handling route options '''
        self.kubeconfig = kubeconfig
        self.name = sname
        self.options = options
        self.fs_group = fs_group
        self.default_add_capabilities = default_add_capabilities
        self.groups = groups
        self.priority = priority
        self.required_drop_capabilities = required_drop_capabilities
        self.run_as_user = run_as_user
        self.se_linux_context = se_linux_context
        self.supplemental_groups = supplemental_groups
        self.users = users
        self.annotations = annotations
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a service as a dict '''
        # allow options
        if self.options:
            for key, value in self.options.items():
                self.data[key] = value
        else:
            self.data['allowHostDirVolumePlugin'] = False
            self.data['allowHostIPC'] = False
            self.data['allowHostNetwork'] = False
            self.data['allowHostPID'] = False
            self.data['allowHostPorts'] = False
            self.data['allowPrivilegedContainer'] = False
            self.data['allowedCapabilities'] = None

        # version
        self.data['apiVersion'] = 'v1'
        # kind
        self.data['kind'] = 'SecurityContextConstraints'
        # defaultAddCapabilities
        self.data['defaultAddCapabilities'] = self.default_add_capabilities
        # fsGroup
        self.data['fsGroup']['type'] = self.fs_group
        # groups
        self.data['groups'] = []
        if self.groups:
            self.data['groups'] = self.groups
        # metadata
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        if self.annotations:
            for key, value in self.annotations.items():
                self.data['metadata'][key] = value
        # priority
        self.data['priority'] = self.priority
        # requiredDropCapabilities
        self.data['requiredDropCapabilities'] = self.required_drop_capabilities
        # runAsUser
        self.data['runAsUser'] = {'type': self.run_as_user}
        # seLinuxContext
        self.data['seLinuxContext'] = {'type': self.se_linux_context}
        # supplementalGroups
        self.data['supplementalGroups'] = {'type': self.supplemental_groups}
        # users
        self.data['users'] = []
        if self.users:
            self.data['users'] = self.users


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class SecurityContextConstraints(Yedit):
    ''' Class to wrap the oc command line tools '''
    default_add_capabilities_path = "defaultAddCapabilities"
    fs_group_path = "fsGroup"
    groups_path = "groups"
    priority_path = "priority"
    required_drop_capabilities_path = "requiredDropCapabilities"
    run_as_user_path = "runAsUser"
    se_linux_context_path = "seLinuxContext"
    supplemental_groups_path = "supplementalGroups"
    users_path = "users"
    kind = 'SecurityContextConstraints'

    def __init__(self, content):
        '''RoleBinding constructor'''
        super(SecurityContextConstraints, self).__init__(content=content)
        self._users = None

    @property
    def users(self):
        ''' users property '''
        if self._users == None:
            self._users = self.get_users()
        return self._users

    @users.setter
    def users(self, data):
        ''' users property setter'''
        self._users = data

    def get_users(self):
        '''get scc users'''
        return self.get(SecurityContextConstraints.users_path) or []

    #### ADD #####
    def add_user(self, inc_user):
        ''' add a subject '''
        if self.users:
            self.users.append(inc_user)
        else:
            self.put(SecurityContextConstraints.users_path, [inc_user])

        return True

    #### /ADD #####

    #### Remove #####
    def remove_user(self, inc_user):
        ''' remove a user '''
        try:
            self.users.remove(inc_user)
        except ValueError as _:
            return False

        return True

    #### /REMOVE #####

    #### UPDATE #####
    def update_user(self, inc_user):
        ''' update a user '''
        try:
            index = self.users.index(inc_user)
        except ValueError as _:
            return self.add_user(inc_user)

        self.users[index] = inc_user

        return True

    #### /UPDATE #####

    #### FIND ####
    def find_user(self, inc_user):
        ''' find a user '''
        index = None
        try:
            index = self.users.index(inc_user)
        except ValueError as _:
            return index

        return index

class OadmPolicyException(Exception):
    ''' Registry Exception Class '''
    pass

class OadmPolicyUserConfig(OpenShiftCLIConfig):
    ''' RegistryConfig is a DTO for the registry.  '''
    def __init__(self, namespace, kubeconfig, policy_options):
        super(OadmPolicyUserConfig, self).__init__(policy_options['name']['value'],
                                                   namespace, kubeconfig, policy_options)
        self.kind = self.get_kind()
        self.namespace = namespace

    def get_kind(self):
        ''' return the kind we are working with '''
        if self.config_options['resource_kind']['value'] == 'role':
            return 'rolebinding'
        elif self.config_options['resource_kind']['value'] == 'cluster-role':
            return 'clusterrolebinding'
        elif self.config_options['resource_kind']['value'] == 'scc':
            return 'scc'

        return None

class OadmPolicyUser(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    def __init__(self,
                 policy_config,
                 verbose=False):
        ''' Constructor for OadmPolicyUser '''
        super(OadmPolicyUser, self).__init__(policy_config.namespace, policy_config.kubeconfig, verbose)
        self.config = policy_config
        self.verbose = verbose
        self._rolebinding = None
        self._scc = None

    @property
    def role_binding(self):
        ''' role_binding property '''
        return self._rolebinding

    @role_binding.setter
    def role_binding(self, binding):
        ''' setter for role_binding property '''
        self._rolebinding = binding

    @property
    def security_context_constraint(self):
        ''' security_context_constraint property '''
        return self._scc

    @security_context_constraint.setter
    def security_context_constraint(self, scc):
        ''' setter for security_context_constraint property '''
        self._scc = scc

    def get(self):
        '''fetch the desired kind'''
        resource_name = self.config.config_options['name']['value']
        if resource_name == 'cluster-reader':
            resource_name += 's'

        return self._get(self.config.kind, resource_name)

    def exists_role_binding(self):
        ''' return whether role_binding exists '''
        results = self.get()
        if results['returncode'] == 0:
            self.role_binding = RoleBinding(results['results'][0])
            if self.role_binding.find_user_name(self.config.config_options['user']['value']) != None:
                return True

            return False

        elif '\"%s\" not found' % self.config.config_options['name']['value'] in results['stderr']:
            return False

        return results

    def exists_scc(self):
        ''' return whether scc exists '''
        results = self.get()
        if results['returncode'] == 0:
            self.security_context_constraint = SecurityContextConstraints(results['results'][0])

            if self.security_context_constraint.find_user(self.config.config_options['user']['value']):
                return True

            return False

        return results

    def exists(self):
        '''does the object exist?'''
        if self.config.config_options['resource_kind']['value'] == 'cluster-role':
            return self.exists_role_binding()

        elif self.config.config_options['resource_kind']['value'] == 'role':
            return self.exists_role_binding()

        elif self.config.config_options['resource_kind']['value'] == 'scc':
            return self.exists_scc()

        return False

    def perform(self):
        '''perform action on resource'''
        cmd = ['-n', self.config.namespace, 'policy',
               self.config.config_options['action']['value'],
               self.config.config_options['name']['value'],
               self.config.config_options['user']['value']]

        return self.openshift_cmd(cmd, oadm=True)
#Manage policy
#
#Usage:
#  oadm policy [options]
#
#Available Commands:
#  add-role-to-user                Add users to a role in the current project
#  remove-role-from-user           Remove user from role in the current project
#  remove-user                     Remove user from the current project
#  add-cluster-role-to-user        Add users to a role for all projects in the cluster
#  remove-cluster-role-from-user   Remove user from role for all projects in the cluster
#  add-scc-to-user                 Add users to a security context constraint
#  remove-scc-from-user            Remove user from scc
#
#Use "oadm help <command>" for more information about a given command.
#Use "oadm options" for a list of global command-line options (applies to all commands).
#

def main():
    '''
    ansible oadm module for user policy
    '''

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present', 'absent']),
            debug=dict(default=False, type='bool'),
            resource_name=dict(required=True, type='str'),
            namespace=dict(default=None, type='str'),
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),

            # add-role-to-user
            user=dict(required=True, type='str'),
            resource_kind=dict(required=True, choices=['role', 'cluster-role', 'scc'], type='str'),
        ),
        supports_check_mode=True,
    )
    state = module.params['state']

    action = None
    if state == 'present':
        action = 'add-' + module.params['resource_kind'] + '-to-user'
    else:
        action = 'remove-' + module.params['resource_kind'] + '-from-user'

    uconfig = OadmPolicyUserConfig(module.params['namespace'],
                                   module.params['kubeconfig'],
                                   {'action': {'value': action, 'include': False},
                                    'user': {'value': module.params['user'], 'include': False},
                                    'resource_kind': {'value': module.params['resource_kind'], 'include': False},
                                    'name': {'value': module.params['resource_name'], 'include': False},
                                   })

    oadmpolicyuser = OadmPolicyUser(uconfig)

    ########
    # Delete
    ########
    if state == 'absent':
        if not oadmpolicyuser.exists():
            module.exit_json(changed=False, state="absent")

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed a delete.')

        api_rval = oadmpolicyuser.perform()

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=True, results=api_rval, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        results = oadmpolicyuser.exists()
        if isinstance(results, dict) and results.has_key('returncode') and results['returncode'] != 0:
            module.fail_json(msg=results)

        if not results:

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            api_rval = oadmpolicyuser.perform()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        module.exit_json(changed=False, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *
main()
