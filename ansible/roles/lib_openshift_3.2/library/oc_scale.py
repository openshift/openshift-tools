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
        cmd = ['get']
        if selector:
            cmd.append('--selector=%s' % selector)
        cmd.extend([resource, '-o', 'json', '-n', self.namespace])
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
            return results['stdout'].split('\n')[0].strip()

        raise OpenShiftCLIError('Problem detecting openshift version.')

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
    re_valid_key = r"(((\[-?\d+\])|([0-9a-zA-Z-./_]+)).?)+$"
    re_key = r"(?:\[(-?\d+)\])|([0-9a-zA-Z-./_]+)"

    def __init__(self, filename=None, content=None, content_type='yaml', backup=False):
        self.content = content
        self.filename = filename
        self.__yaml_dict = content
        self.content_type = content_type
        self.backup = backup
        if self.filename and not self.content:
            if not self.load(content_type=self.content_type):
                self.__yaml_dict = {}

    @property
    def yaml_dict(self):
        ''' getter method for yaml_dict '''
        return self.__yaml_dict

    @yaml_dict.setter
    def yaml_dict(self, value):
        ''' setter method for yaml_dict '''
        self.__yaml_dict = value

    @staticmethod
    def remove_entry(data, key):
        ''' remove data at location key '''
        if key == '' and isinstance(data, dict):
            data.clear()
            return True
        elif key == '' and isinstance(data, list):
            del data[:]
            return True

        if not (key and re.match(Yedit.re_valid_key, key) and isinstance(data, (list, dict))):
            return None

        key_indexes = re.findall(Yedit.re_key, key)
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
    def add_entry(data, key, item=None):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            key = a#b
            return c
        '''
        if key == '':
            pass
        elif not (key and re.match(Yedit.re_valid_key, key) and isinstance(data, (list, dict))):
            return None

        key_indexes = re.findall(Yedit.re_key, key)
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
    def get_entry(data, key):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            key = a.b
            return c
        '''
        if key == '':
            pass
        elif not (key and re.match(Yedit.re_valid_key, key) and isinstance(data, (list, dict))):
            return None

        key_indexes = re.findall(Yedit.re_key, key)
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
            entry = Yedit.get_entry(self.yaml_dict, key)
        except KeyError as _:
            entry = None

        return entry

    def pop(self, path, key_or_item):
        ''' remove a key, value pair from a dict or an item for a list'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
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
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == None:
            return  (False, self.yaml_dict)

        result = Yedit.remove_entry(self.yaml_dict, path)
        if not result:
            return (False, self.yaml_dict)

        return (True, self.yaml_dict)

    def exists(self, path, value):
        ''' check if value exists at path'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
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
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == None or not isinstance(entry, list):
            return (False, self.yaml_dict)

        # pylint: disable=no-member,maybe-no-member
        entry.append(value)
        return (True, self.yaml_dict)

    def update(self, path, value, index=None, curr_value=None):
        ''' put path, value into a dict '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
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
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == value:
            return (False, self.yaml_dict)

        tmp_copy = copy.deepcopy(self.yaml_dict)
        result = Yedit.add_entry(tmp_copy, path, value)
        if not result:
            return (False, self.yaml_dict)

        self.yaml_dict = tmp_copy

        return (True, self.yaml_dict)

    def create(self, path, value):
        ''' create a yaml file '''
        if not self.file_exists():
            tmp_copy = copy.deepcopy(self.yaml_dict)
            result = Yedit.add_entry(tmp_copy, path, value)
            if result:
                self.yaml_dict = tmp_copy
                return (True, self.yaml_dict)

        return (False, self.yaml_dict)

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

    replicas_path = "spec#replicas"
    env_path = "spec#template#spec#containers[0]#env"
    volumes_path = "spec#template#spec#volumes"
    container_path = "spec#template#spec#containers"
    volume_mounts_path = "spec#template#spec#containers[0]#volumeMounts"

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
# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCScale(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 resource_name,
                 namespace,
                 replicas,
                 kind,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OCScale '''
        super(OCScale, self).__init__(namespace, kubeconfig)
        self.kind = kind
        self.replicas = replicas
        self.name = resource_name
        self.namespace = namespace
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._resource = None

    @property
    def resource(self):
        ''' property function for resource var '''
        if not self._resource:
            self.get()
        return self._resource

    @resource.setter
    def resource(self, data):
        ''' setter function for resource var '''
        self._resource = data

    def get(self):
        '''return replicas information '''
        vol = self._get(self.kind, self.name)
        if vol['returncode'] == 0:
            if self.kind == 'dc':
                self.resource = DeploymentConfig(content=vol['results'][0])
                vol['results'] = [self.resource.get_replicas()]

        return vol

    def put(self):
        '''update replicas into dc '''
        self.resource.update_replicas(self.replicas)
        #self.resource.get_volumes()
        #self.resource.update_volume_mount(self.volume_mount)
        return self._replace_content(self.kind, self.name, self.resource.yaml_dict)

    def needs_update(self):
        ''' verify whether an update is needed '''
        return self.resource.needs_update_replicas(self.replicas)
# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

def main():
    '''
    ansible oc module for scaling
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'list']),
            debug=dict(default=False, type='bool'),
            kind=dict(default='dc', choices=['dc', 'rc'], type='str'),
            namespace=dict(default='default', type='str'),
            replicas=dict(default=None, type='int'),
            name=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )
    oc_scale = OCScale(module.params['name'],
                       module.params['namespace'],
                       module.params['replicas'],
                       module.params['kind'],
                       module.params['kubeconfig'],
                       verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_scale.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    if state == 'present':
        ########
        # Update
        ########
        if oc_scale.needs_update():
            api_rval = oc_scale.put()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_scale.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval['results'], state="present")

        module.exit_json(changed=False, results=api_rval['results'], state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
