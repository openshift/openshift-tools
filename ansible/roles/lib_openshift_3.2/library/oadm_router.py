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
        '''return a secret by name '''
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

    def _get_version(self):
        ''' return the version of openshift '''
        results = self.openshift_cmd(['version'], output=True, output_type='raw')
        if results['returncode'] == 0:
            versions = {}
            for line in results['results'].strip().split('\n'):
                name, version = line.split()
                versions[name] = version

            rval = {}
            rval['returncode'] = results['returncode']
            rval.update(versions)
            return rval

        raise OpenShiftCLIError('Problem detecting openshift version.')

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
        if self.filename and not self.content:
            if not self.load(content_type=self.content_type):
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
        ''' write to file '''
        # check if it exists
        if not self.file_exists():
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

        if not contents:
            return None

        # check if it is yaml
        try:
            if content_type == 'yaml':
                self.yaml_dict = yaml.load(contents)
            elif content_type == 'json':
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
class ServiceConfig(object):
    ''' Handle service options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 ports,
                 selector=None,
                 labels=None,
                 cluster_ip=None,
                 portal_ip=None,
                 session_affinity=None,
                 service_type=None):
        ''' constructor for handling service options '''
        self.name = sname
        self.namespace = namespace
        self.ports = ports
        self.selector = selector
        self.labels = labels
        self.cluster_ip = cluster_ip
        self.portal_ip = portal_ip
        self.session_affinity = session_affinity
        self.service_type = service_type
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a service as a dict '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = 'Service'
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        self.data['metadata']['namespace'] = self.namespace
        if self.labels:
            for lab, lab_value  in self.labels.items():
                self.data['metadata'][lab] = lab_value
        self.data['spec'] = {}

        if self.ports:
            self.data['spec']['ports'] = self.ports
        else:
            self.data['spec']['ports'] = []

        if self.selector:
            self.data['spec']['selector'] = self.selector

        self.data['spec']['sessionAffinity'] = self.session_affinity or 'None'

        if self.cluster_ip:
            self.data['spec']['clusterIP'] = self.cluster_ip

        if self.portal_ip:
            self.data['spec']['portalIP'] = self.portal_ip

        if self.service_type:
            self.data['spec']['type'] = self.service_type

# pylint: disable=too-many-instance-attributes,too-many-public-methods
class Service(Yedit):
    ''' Class to wrap the oc command line tools '''
    port_path = "spec.ports"
    portal_ip = "spec.portalIP"
    cluster_ip = "spec.clusterIP"
    kind = 'Service'

    def __init__(self, content):
        '''Service constructor'''
        super(Service, self).__init__(content=content)

    def get_ports(self):
        ''' get a list of ports '''
        return self.get(Service.port_path) or []

    def add_ports(self, inc_ports):
        ''' add a port object to the ports list '''
        if not isinstance(inc_ports, list):
            inc_ports = [inc_ports]

        ports = self.get_ports()
        if not ports:
            self.put(Service.port_path, inc_ports)
        else:
            ports.extend(inc_ports)

        return True

    def find_ports(self, inc_port):
        ''' find a specific port '''
        for port in self.get_ports():
            if port['port'] == inc_port['port']:
                return port

        return None

    def delete_ports(self, inc_ports):
        ''' remove a port from a service '''
        if not isinstance(inc_ports, list):
            inc_ports = [inc_ports]

        ports = self.get(Service.port_path) or []

        if not ports:
            return True

        removed = False
        for inc_port in inc_ports:
            port = self.find_ports(inc_port)
            if port:
                ports.remove(port)
                removed = True

        return removed

    def add_cluster_ip(self, sip):
        '''add cluster ip'''
        self.put(Service.cluster_ip, sip)

    def add_portal_ip(self, pip):
        '''add cluster ip'''
        self.put(Service.portal_ip, pip)



# pylint: disable=too-many-public-methods
class DeploymentConfig(Yedit):
    ''' Class to wrap the oc command line tools '''
    default_deployment_config = '''
apiVersion: v1
kind: DeploymentConfig
metadata:
  name: default_dc
  namespace: default
spec:
  replicas: 0
  selector:
    default_dc: default_dc
  strategy:
    resources: {}
    rollingParams:
      intervalSeconds: 1
      maxSurge: 0
      maxUnavailable: 25%
      timeoutSeconds: 600
      updatePercent: -25
      updatePeriodSeconds: 1
    type: Rolling
  template:
    metadata:
    spec:
      containers:
      - env:
        - name: default
          value: default
        image: default
        imagePullPolicy: IfNotPresent
        name: default_dc
        ports:
        - containerPort: 8000
          hostPort: 8000
          protocol: TCP
          name: default_port
        resources: {}
        terminationMessagePath: /dev/termination-log
      dnsPolicy: ClusterFirst
      hostNetwork: true
      nodeSelector:
        type: compute
      restartPolicy: Always
      securityContext: {}
      serviceAccount: default
      serviceAccountName: default
      terminationGracePeriodSeconds: 30
  triggers:
  - type: ConfigChange
'''

    replicas_path = "spec.replicas"
    env_path = "spec.template.spec.containers[0].env"
    volumes_path = "spec.template.spec.volumes"
    container_path = "spec.template.spec.containers"
    volume_mounts_path = "spec.template.spec.containers[0].volumeMounts"

    def __init__(self, content=None):
        ''' Constructor for OpenshiftOC '''
        if not content:
            content = DeploymentConfig.default_deployment_config

        super(DeploymentConfig, self).__init__(content=content)

    # pylint: disable=no-member
    def add_env_value(self, key, value):
        ''' add key, value pair to env array '''
        rval = False
        env = self.get_env_vars()
        if env:
            env.append({'name': key, 'value': value})
            rval = True
        else:
            result = self.put(DeploymentConfig.env_path, {'name': key, 'value': value})
            rval = result[0]

        return rval

    def exists_env_value(self, key, value):
        ''' return whether a key, value  pair exists '''
        results = self.get_env_vars()
        if not results:
            return False

        for result in results:
            if result['name'] == key and result['value'] == value:
                return True

        return False

    def exists_env_key(self, key):
        ''' return whether a key, value  pair exists '''
        results = self.get_env_vars()
        if not results:
            return False

        for result in results:
            if result['name'] == key:
                return True

        return False

    def get_env_vars(self):
        '''return a environment variables '''
        return self.get(DeploymentConfig.env_path) or []

    def delete_env_var(self, keys):
        '''delete a list of keys '''
        if not isinstance(keys, list):
            keys = [keys]

        env_vars_array = self.get_env_vars()
        modified = False
        idx = None
        for key in keys:
            for env_idx, env_var in enumerate(env_vars_array):
                if env_var['name'] == key:
                    idx = env_idx
                    break

            if idx:
                modified = True
                del env_vars_array[idx]

        if modified:
            return True

        return False

    def update_env_var(self, key, value):
        '''place an env in the env var list'''

        env_vars_array = self.get_env_vars()
        idx = None
        for env_idx, env_var in enumerate(env_vars_array):
            if env_var['name'] == key:
                idx = env_idx
                break

        if idx:
            env_vars_array[idx]['value'] = value
        else:
            self.add_env_value(key, value)

        return True

    def exists_volume_mount(self, volume_mount):
        ''' return whether a volume mount exists '''
        exist_volume_mounts = self.get_volume_mounts()

        if not exist_volume_mounts:
            return False

        volume_mount_found = False
        for exist_volume_mount in exist_volume_mounts:
            if exist_volume_mount['name'] == volume_mount['name']:
                volume_mount_found = True
                break

        return volume_mount_found

    def exists_volume(self, volume):
        ''' return whether a volume exists '''
        exist_volumes = self.get_volumes()

        volume_found = False
        for exist_volume in exist_volumes:
            if exist_volume['name'] == volume['name']:
                volume_found = True
                break

        return volume_found

    def find_volume_by_name(self, volume, mounts=False):
        ''' return the index of a volume '''
        volumes = []
        if mounts:
            volumes = self.get_volume_mounts()
        else:
            volumes = self.get_volumes()
        for exist_volume in volumes:
            if exist_volume['name'] == volume['name']:
                return exist_volume

        return None

    def get_replicas(self):
        ''' return replicas setting '''
        return self.get(DeploymentConfig.replicas_path)

    def get_volume_mounts(self):
        '''return volume mount information '''
        return self.get_volumes(mounts=True)

    def get_volumes(self, mounts=False):
        '''return volume mount information '''
        if mounts:
            return self.get(DeploymentConfig.volume_mounts_path) or []

        return self.get(DeploymentConfig.volumes_path) or []

    def delete_volume_by_name(self, volume):
        '''delete a volume '''
        modified = False
        exist_volume_mounts = self.get_volume_mounts()
        exist_volumes = self.get_volumes()
        del_idx = None
        for idx, exist_volume in enumerate(exist_volumes):
            if exist_volume.has_key('name') and exist_volume['name'] == volume['name']:
                del_idx = idx
                break

        if del_idx != None:
            del exist_volumes[del_idx]
            modified = True

        del_idx = None
        for idx, exist_volume_mount in enumerate(exist_volume_mounts):
            if exist_volume_mount.has_key('name') and exist_volume_mount['name'] == volume['name']:
                del_idx = idx
                break

        if del_idx != None:
            del exist_volume_mounts[idx]
            modified = True

        return modified

    def add_volume_mount(self, volume_mount):
        ''' add a volume or volume mount to the proper location '''
        exist_volume_mounts = self.get_volume_mounts()

        if not exist_volume_mounts and volume_mount:
            self.put(DeploymentConfig.volume_mounts_path, [volume_mount])
        else:
            exist_volume_mounts.append(volume_mount)

    def add_volume(self, volume):
        ''' add a volume or volume mount to the proper location '''
        exist_volumes = self.get_volumes()
        if not volume:
            return

        if not exist_volumes:
            self.put(DeploymentConfig.volumes_path, [volume])
        else:
            exist_volumes.append(volume)

    def update_replicas(self, replicas):
        ''' update replicas value '''
        self.put(DeploymentConfig.replicas_path, replicas)

    def update_volume(self, volume):
        '''place an env in the env var list'''
        exist_volumes = self.get_volumes()

        if not volume:
            return False

        # update the volume
        update_idx = None
        for idx, exist_vol in enumerate(exist_volumes):
            if exist_vol['name'] == volume['name']:
                update_idx = idx
                break

        if update_idx != None:
            exist_volumes[update_idx] = volume
        else:
            self.add_volume(volume)

        return True

    def update_volume_mount(self, volume_mount):
        '''place an env in the env var list'''
        modified = False

        exist_volume_mounts = self.get_volume_mounts()

        if not volume_mount:
            return False

        # update the volume mount
        for exist_vol_mount in exist_volume_mounts:
            if exist_vol_mount['name'] == volume_mount['name']:
                if exist_vol_mount.has_key('mountPath') and \
                   str(exist_vol_mount['mountPath']) != str(volume_mount['mountPath']):
                    exist_vol_mount['mountPath'] = volume_mount['mountPath']
                    modified = True
                break

        if not modified:
            self.add_volume_mount(volume_mount)
            modified = True

        return modified

    def needs_update_volume(self, volume, volume_mount):
        ''' verify a volume update is needed '''
        exist_volume = self.find_volume_by_name(volume)
        exist_volume_mount = self.find_volume_by_name(volume, mounts=True)
        results = []
        results.append(exist_volume['name'] == volume['name'])

        if volume.has_key('secret'):
            results.append(exist_volume.has_key('secret'))
            results.append(exist_volume['secret']['secretName'] == volume['secret']['secretName'])
            results.append(exist_volume_mount['name'] == volume_mount['name'])
            results.append(exist_volume_mount['mountPath'] == volume_mount['mountPath'])

        elif volume.has_key('emptyDir'):
            results.append(exist_volume_mount['name'] == volume['name'])
            results.append(exist_volume_mount['mountPath'] == volume_mount['mountPath'])

        elif volume.has_key('persistentVolumeClaim'):
            pvc = 'persistentVolumeClaim'
            results.append(exist_volume.has_key(pvc))
            if results[-1]:
                results.append(exist_volume[pvc]['claimName'] == volume[pvc]['claimName'])

                if volume[pvc].has_key('claimSize'):
                    results.append(exist_volume[pvc]['claimSize'] == volume[pvc]['claimSize'])

        elif volume.has_key('hostpath'):
            results.append(exist_volume.has_key('hostPath'))
            results.append(exist_volume['hostPath']['path'] == volume_mount['mountPath'])

        return not all(results)

    def needs_update_replicas(self, replicas):
        ''' verify whether a replica update is needed '''
        current_reps = self.get(DeploymentConfig.replicas_path)
        return not current_reps == replicas

# pylint: disable=too-many-instance-attributes
class SecretConfig(object):
    ''' Handle secret options '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 sname,
                 namespace,
                 kubeconfig,
                 secrets=None):
        ''' constructor for handling secret options '''
        self.kubeconfig = kubeconfig
        self.name = sname
        self.namespace = namespace
        self.secrets = secrets
        self.data = {}

        self.create_dict()

    def create_dict(self):
        ''' return a secret as a dict '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = 'Secret'
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        self.data['metadata']['namespace'] = self.namespace
        self.data['data'] = {}
        if self.secrets:
            for key, value in self.secrets.items():
                self.data['data'][key] = value

# pylint: disable=too-many-instance-attributes
class Secret(Yedit):
    ''' Class to wrap the oc command line tools '''
    secret_path = "data"
    kind = 'secret'

    def __init__(self, content):
        '''secret constructor'''
        super(Secret, self).__init__(content=content)
        self._secrets = None

    @property
    def secrets(self):
        '''secret property'''
        if self._secrets == None:
            self._secrets = self.get_secrets()
        return self._secrets

    @secrets.setter
    def secrets(self):
        '''secret property setter'''
        if self._secrets == None:
            self._secrets = self.get_secrets()
        return self._secrets

    def get_secrets(self):
        ''' return cert '''
        return self.get(Secret.secret_path) or {}

    def add_secret(self, key, value):
        ''' return cert '''
        if self.secrets:
            self.secrets[key] = value
        else:
            self.put(Secret.secret_path, {key: value})

        return True

    def delete_secret(self, key):
        ''' delete secret'''
        try:
            del self.secrets[key]
        except KeyError as _:
            return False

        return True

    def find_secret(self, key):
        ''' find secret'''
        rval = None
        try:
            rval = self.secrets[key]
        except KeyError as _:
            return None

        return {'key': key, 'value': rval}

    def update_secret(self, key, value):
        ''' update a secret'''
        if self.secrets.has_key(key):
            self.secrets[key] = value
        else:
            self.add_secret(key, value)

        return True

class ServiceAccountConfig(object):
    '''Service account config class

       This class stores the options and returns a default service account
    '''

    # pylint: disable=too-many-arguments
    def __init__(self, sname, namespace, kubeconfig, secrets=None, image_pull_secrets=None):
        self.name = sname
        self.kubeconfig = kubeconfig
        self.namespace = namespace
        self.secrets = secrets or []
        self.image_pull_secrets = image_pull_secrets or []
        self.data = {}
        self.create_dict()

    def create_dict(self):
        ''' return a properly structured volume '''
        self.data['apiVersion'] = 'v1'
        self.data['kind'] = 'ServiceAccount'
        self.data['metadata'] = {}
        self.data['metadata']['name'] = self.name
        self.data['metadata']['namespace'] = self.namespace

        self.data['secrets'] = []
        if self.secrets:
            for sec in self.secrets:
                self.data['secrets'].append({"name": sec})

        self.data['imagePullSecrets'] = []
        if self.image_pull_secrets:
            for sec in self.image_pull_secrets:
                self.data['imagePullSecrets'].append({"name": sec})

class ServiceAccount(Yedit):
    ''' Class to wrap the oc command line tools '''
    image_pull_secrets_path = "imagePullSecrets"
    secrets_path = "secrets"

    def __init__(self, content):
        '''ServiceAccount constructor'''
        super(ServiceAccount, self).__init__(content=content)
        self._secrets = None
        self._image_pull_secrets = None

    @property
    def image_pull_secrets(self):
        ''' property for image_pull_secrets '''
        if self._image_pull_secrets == None:
            self._image_pull_secrets = self.get(ServiceAccount.image_pull_secrets_path) or []
        return self._image_pull_secrets

    @image_pull_secrets.setter
    def image_pull_secrets(self, secrets):
        ''' property for secrets '''
        self._image_pull_secrets = secrets

    @property
    def secrets(self):
        ''' property for secrets '''
        print "Getting secrets property"
        if not self._secrets:
            self._secrets = self.get(ServiceAccount.secrets_path) or []
        return self._secrets

    @secrets.setter
    def secrets(self, secrets):
        ''' property for secrets '''
        self._secrets = secrets

    def delete_secret(self, inc_secret):
        ''' remove a secret '''
        remove_idx = None
        for idx, sec in enumerate(self.secrets):
            if sec['name'] == inc_secret:
                remove_idx = idx
                break

        if remove_idx:
            del self.secrets[remove_idx]
            return True

        return False

    def delete_image_pull_secret(self, inc_secret):
        ''' remove a image_pull_secret '''
        remove_idx = None
        for idx, sec in enumerate(self.image_pull_secrets):
            if sec['name'] == inc_secret:
                remove_idx = idx
                break

        if remove_idx:
            del self.image_pull_secrets[remove_idx]
            return True

        return False

    def find_secret(self, inc_secret):
        '''find secret'''
        for secret in self.secrets:
            if secret['name'] == inc_secret:
                return secret

        return None

    def find_image_pull_secret(self, inc_secret):
        '''find secret'''
        for secret in self.image_pull_secrets:
            if secret['name'] == inc_secret:
                return secret

        return None

    def add_secret(self, inc_secret):
        '''add secret'''
        if self.secrets:
            self.secrets.append({"name": inc_secret})
        else:
            self.put(ServiceAccount.secrets_path, [{"name": inc_secret}])

    def add_image_pull_secret(self, inc_secret):
        '''add image_pull_secret'''
        if self.image_pull_secrets:
            self.image_pull_secrets.append({"name": inc_secret})
        else:
            self.put(ServiceAccount.image_pull_secrets_path, [{"name": inc_secret}])

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

import time

class RouterException(Exception):
    ''' Router exception'''
    pass

class RouterConfig(OpenShiftCLIConfig):
    ''' RouterConfig is a DTO for the router.  '''
    def __init__(self, rname, namespace, kubeconfig, router_options):
        super(RouterConfig, self).__init__(rname, namespace, kubeconfig, router_options)

class Router(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    def __init__(self,
                 router_config,
                 verbose=False):
        ''' Constructor for OpenshiftOC

           a router consists of 3 or more parts
           - dc/router
           - svc/router
           - endpoint/router
        '''
        super(Router, self).__init__('default', router_config.kubeconfig, verbose)
        self.config = router_config
        self.verbose = verbose
        self.router_parts = [{'kind': 'dc', 'name': self.config.name},
                             {'kind': 'svc', 'name': self.config.name},
                             {'kind': 'sa', 'name': self.config.name},
                             {'kind': 'secret', 'name': 'router-certs'},
                             {'kind': 'clusterrolebinding', 'name': 'router-router-role'},
                             #{'kind': 'endpoints', 'name': self.config.name},
                            ]

        self.__router_prep = None
        self.dconfig = None
        self.svc = None
        self._secret = None
        self._serviceaccount = None
        self._rolebinding = None
        self.get()

    @property
    def router_prep(self):
        ''' property deploymentconfig'''
        if self.__router_prep == None:
            results = self.prepare_router()
            if not results:
                raise RouterException('Could not perform router preparation')
            self.__router_prep = results

        return self.__router_prep

    @router_prep.setter
    def router_prep(self, obj):
        '''set the router prep property'''
        self.__router_prep = obj

    @property
    def deploymentconfig(self):
        ''' property deploymentconfig'''
        return self.dconfig

    @deploymentconfig.setter
    def deploymentconfig(self, config):
        ''' setter for property deploymentconfig '''
        self.dconfig = config

    @property
    def service(self):
        ''' property service '''
        return self.svc

    @service.setter
    def service(self, config):
        ''' setter for property service '''
        self.svc = config

    @property
    def secret(self):
        ''' property secret '''
        return self._secret

    @secret.setter
    def secret(self, config):
        ''' setter for property secret '''
        self._secret = config

    @property
    def serviceaccount(self):
        ''' property secret '''
        return self._serviceaccount

    @serviceaccount.setter
    def serviceaccount(self, config):
        ''' setter for property secret '''
        self._serviceaccount = config

    @property
    def rolebinding(self):
        ''' property rolebinding '''
        return self._rolebinding

    @rolebinding.setter
    def rolebinding(self, config):
        ''' setter for property rolebinding '''
        self._rolebinding = config

    def get(self):
        ''' return the self.router_parts '''
        self.service = None
        self.deploymentconfig = None
        self.serviceaccount = None
        self.secret = None
        self.rolebinding = None
        for part in self.router_parts:
            result = self._get(part['kind'], rname=part['name'])
            if result['returncode'] == 0 and part['kind'] == 'dc':
                self.deploymentconfig = DeploymentConfig(result['results'][0])
            elif result['returncode'] == 0 and part['kind'] == 'svc':
                self.service = Service(content=result['results'][0])
            elif result['returncode'] == 0 and part['kind'] == 'sa':
                self.serviceaccount = ServiceAccount(content=result['results'][0])
            elif result['returncode'] == 0 and part['kind'] == 'secret':
                self.secret = Secret(content=result['results'][0])
            elif result['returncode'] == 0 and part['kind'] == 'clusterrolebinding':
                self.rolebinding = RoleBinding(content=result['results'][0])

        return {'deploymentconfig': self.deploymentconfig,
                'service': self.service,
                'serviceaccount': self.serviceaccount,
                'secret': self.secret,
                'clusterrolebinding': self.rolebinding,
               }

    def exists(self):
        '''return a whether svc or dc exists '''
        if self.deploymentconfig and self.service and self.secret and self.serviceaccount:
            return True

        return False

    def delete(self):
        '''return all pods '''
        parts = []
        for part in self.router_parts:
            parts.append(self._delete(part['kind'], part['name']))

        return parts

    def add_modifications(self, deploymentconfig):
        '''modify the deployment config'''
        # We want modifications in the form of edits coming in from the module.
        # Let's apply these here
        edit_results = []
        for key, value in self.config.config_options['edits'].get('value', {}).items():
            edit_results.append(deploymentconfig.put(key, value))

        if not any([res[0] for res in edit_results]):
            return None

        return deploymentconfig.yaml_dict

    def prepare_router(self):
        '''prepare router for instantiation'''
        # We need to create the pem file
        router_pem = '/tmp/router.pem'
        with open(router_pem, 'w') as rfd:
            rfd.write(open(self.config.config_options['cert_file']['value']).read())
            rfd.write(open(self.config.config_options['key_file']['value']).read())
            if self.config.config_options['cacert_file']['value'] and \
               os.path.exists(self.config.config_options['cacert_file']['value']):
                rfd.write(open(self.config.config_options['cacert_file']['value']).read())

        atexit.register(Utils.cleanup, [router_pem])
        self.config.config_options['default_cert']['value'] = router_pem

        options = self.config.to_option_list()

        cmd = ['router', '-n', self.config.namespace]
        cmd.extend(options)
        cmd.extend(['--dry-run=True', '-o', 'json'])

        results = self.openshift_cmd(cmd, oadm=True, output=True, output_type='json')

        # pylint: disable=no-member
        if results['returncode'] != 0 and results['results'].has_key('items'):
            return results

        oc_objects = {'DeploymentConfig': {'obj': None, 'path': None},
                      'Secret': {'obj': None, 'path': None},
                      'ServiceAccount': {'obj': None, 'path': None},
                      'ClusterRoleBinding': {'obj': None, 'path': None},
                      'Service': {'obj': None, 'path': None},
                     }
        # pylint: disable=invalid-sequence-index
        for res in results['results']['items']:
            if res['kind'] == 'DeploymentConfig':
                oc_objects['DeploymentConfig']['obj'] = DeploymentConfig(res)
            elif res['kind'] == 'Service':
                oc_objects['Service']['obj'] = Service(res)
            elif res['kind'] == 'ServiceAccount':
                oc_objects['ServiceAccount']['obj'] = ServiceAccount(res)
            elif res['kind'] == 'Secret':
                oc_objects['Secret']['obj'] = Secret(res)
            elif res['kind'] == 'ClusterRoleBinding':
                oc_objects['ClusterRoleBinding']['obj'] = RoleBinding(res)

        # Currently only deploymentconfig needs updating
        # Verify we got a deploymentconfig
        if not oc_objects['DeploymentConfig']['obj']:
            return results

        # results will need to get parsed here and modifications added
        tmp_dc = self.add_modifications(oc_objects['DeploymentConfig']['obj'])
        oc_objects['DeploymentConfig']['obj'] = DeploymentConfig(tmp_dc)

        for oc_type in oc_objects.keys():
            oc_objects[oc_type]['path'] = Utils.create_file(oc_type, oc_objects[oc_type]['obj'].yaml_dict)

        return oc_objects

    def create(self):
        '''Create a deploymentconfig '''
        # generate the objects and prepare for instantiation
        self.prepare_router()

        results = []
        for _, oc_data in self.router_prep.items():
            results.append(self._create(oc_data['path']))

        rval = 0
        for result in results:
            if result['returncode'] != 0 and not 'already exist' in result['stderr']:
                rval = result['returncode']

        return {'returncode': rval, 'results': results}

    def update(self):
        '''run update for the router.  This performs a delete and then create '''
        parts = self.delete()
        for part in parts:
            if part['returncode'] != 0:
                if part.has_key('stderr') and 'not found' in part['stderr']:
                    # the object is not there, continue
                    continue

                # something went wrong
                return parts

        # Ugly built in sleep here.
        time.sleep(15)

        return self.create()

    # pylint: disable=too-many-return-statements,too-many-branches
    def needs_update(self, verbose=False):
        ''' check to see if we need to update '''
        if not self.deploymentconfig or not self.service or not self.serviceaccount or not self.secret:
            return True

        oc_objects_prep = self.prepare_router()

        # Since the output from oadm_router is returned as raw
        # we need to parse it.  The first line is the stats_password in 3.1
        # Inside of 3.2, it is just json

        # ServiceAccount:
        #   Need to determine the pregenerated ones from the original
        #   Since these are auto generated, we can skip
        skip = ['secrets', 'imagePullSecrets']
        if not Utils.check_def_equal(oc_objects_prep['ServiceAccount']['obj'].yaml_dict,
                                     self.serviceaccount.yaml_dict,
                                     skip_keys=skip,
                                     debug=verbose):
            return True

        # Secret:
        #   In 3.2 oadm router generates a secret volume for certificates
        #   See if one was generated from our dry-run and verify it if needed
        if oc_objects_prep['Secret']['obj']:
            if not self.secret:
                return True
            if not Utils.check_def_equal(oc_objects_prep['Secret']['obj'].yaml_dict,
                                         self.secret.yaml_dict,
                                         skip_keys=skip,
                                         debug=verbose):
                return True

        # Service:
        #   Fix the ports to have protocol=TCP
        for port in oc_objects_prep['Service']['obj'].get('spec.ports'):
            port['protocol'] = 'TCP'

        skip = ['portalIP', 'clusterIP', 'sessionAffinity', 'type']
        if not Utils.check_def_equal(oc_objects_prep['Service']['obj'].yaml_dict,
                                     self.service.yaml_dict,
                                     skip_keys=skip,
                                     debug=verbose):
            return True

        # DeploymentConfig:
        #   Router needs some exceptions.
        #   We do not want to check the autogenerated password for stats admin
        if not self.config.config_options['stats_password']['value']:
            for idx, env_var in enumerate(oc_objects_prep['DeploymentConfig']['obj'].get(\
                        'spec.template.spec.containers[0].env') or []):
                if env_var['name'] == 'STATS_PASSWORD':
                    env_var['value'] = \
                      self.deploymentconfig.get('spec.template.spec.containers[0].env[%s].value' % idx)
                    break

        #   dry-run doesn't add the protocol to the ports section.  We will manually do that.
        for idx, port in enumerate(oc_objects_prep['DeploymentConfig']['obj'].get(\
                        'spec.template.spec.containers[0].ports') or []):
            if not port.has_key('protocol'):
                port['protocol'] = 'TCP'

        #   These are different when generating
        skip = ['dnsPolicy',
                'terminationGracePeriodSeconds',
                'restartPolicy', 'timeoutSeconds',
                'livenessProbe', 'readinessProbe',
                'terminationMessagePath', 'hostPort',
               ]

        return not Utils.check_def_equal(oc_objects_prep['DeploymentConfig']['obj'].yaml_dict,
                                         self.deploymentconfig.yaml_dict,
                                         skip_keys=skip,
                                         debug=True)



def main():
    '''
    ansible oc module for router
    '''

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present', 'absent']),
            debug=dict(default=False, type='bool'),
            namespace=dict(default='default', type='str'),
            name=dict(default='router', type='str'),

            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            cert_file=dict(default=None, type='str'),
            key_file=dict(default=None, type='str'),
            images=dict(default=None, type='str'), #'openshift3/ose-${component}:${version}'
            latest_image=dict(default=False, type='bool'),
            labels=dict(default=None, type='list'),
            ports=dict(default=['80:80', '443:443'], type='list'),
            replicas=dict(default=1, type='int'),
            selector=dict(default=None, type='str'),
            service_account=dict(default='router', type='str'),
            router_type=dict(default='haproxy-router', type='str'),
            host_network=dict(default=True, type='bool'),
            # external host options
            external_host=dict(default=None, type='str'),
            external_host_vserver=dict(default=None, type='str'),
            external_host_insecure=dict(default=False, type='bool'),
            external_host_partition_path=dict(default=None, type='str'),
            external_host_username=dict(default=None, type='str'),
            external_host_password=dict(default=None, type='str'),
            external_host_private_key=dict(default=None, type='str'),
            # Metrics
            expose_metrics=dict(default=False, type='bool'),
            metrics_image=dict(default=None, type='str'),
            # Stats
            stats_user=dict(default=None, type='str'),
            stats_password=dict(default=None, type='str'),
            stats_port=dict(default=1936, type='int'),
            # extra
            cacert_file=dict(default=None, type='str'),
            # edits
            edits=dict(default={}, type='dict'),
        ),
        mutually_exclusive=[["router_type", "images"]],

        supports_check_mode=True,
    )

    rconfig = RouterConfig(module.params['name'],
                           module.params['namespace'],
                           module.params['kubeconfig'],
                           {'default_cert': {'value': None, 'include': True},
                            'cert_file': {'value': module.params['cert_file'], 'include': False},
                            'key_file': {'value': module.params['key_file'], 'include': False},
                            'images': {'value': module.params['images'], 'include': True},
                            'latest_image': {'value': module.params['latest_image'], 'include': True},
                            'labels': {'value': module.params['labels'], 'include': True},
                            'ports': {'value': ','.join(module.params['ports']), 'include': True},
                            'replicas': {'value': module.params['replicas'], 'include': True},
                            'selector': {'value': module.params['selector'], 'include': True},
                            'service_account': {'value': module.params['service_account'], 'include': True},
                            'router_type': {'value': module.params['router_type'], 'include': False},
                            'host_network': {'value': module.params['host_network'], 'include': True},
                            'external_host': {'value': module.params['external_host'], 'include': True},
                            'external_host_vserver': {'value': module.params['external_host_vserver'],
                                                      'include': True},
                            'external_host_insecure': {'value': module.params['external_host_insecure'],
                                                       'include': True},
                            'external_host_partition_path': {'value': module.params['external_host_partition_path'],
                                                             'include': True},
                            'external_host_username': {'value': module.params['external_host_username'],
                                                       'include': True},
                            'external_host_password': {'value': module.params['external_host_password'],
                                                       'include': True},
                            'external_host_private_key': {'value': module.params['external_host_private_key'],
                                                          'include': True},
                            'expose_metrics': {'value': module.params['expose_metrics'], 'include': True},
                            'metrics_image': {'value': module.params['metrics_image'], 'include': True},
                            'stats_user': {'value': module.params['stats_user'], 'include': True},
                            'stats_password': {'value': module.params['stats_password'], 'include': True},
                            'stats_port': {'value': module.params['stats_port'], 'include': True},
                            # extra
                            'cacert_file': {'value': module.params['cacert_file'], 'include': False},
                            # edits
                            'edits': {'value': module.params['edits'], 'include': False},
                           })


    ocrouter = Router(rconfig)

    state = module.params['state']

    ########
    # Delete
    ########
    if state == 'absent':
        if not ocrouter.exists():
            module.exit_json(changed=False, state="absent")

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed a delete.')

        api_rval = ocrouter.delete()
        module.exit_json(changed=True, results=api_rval, state="absent")


    if state == 'present':
        ########
        # Create
        ########
        if not ocrouter.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            api_rval = ocrouter.create()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if not ocrouter.needs_update():
            module.exit_json(changed=False, state="present")

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed an update.')

        api_rval = ocrouter.update()

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=True, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
