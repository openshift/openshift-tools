#!/usr/bin/env python
"""
    Playbook Executor used to launch ansible playbooks
"""
from __future__ import print_function
import datetime
import os
import subprocess

class PlaybookExecutor(object):
    """ Helper class to execute playbooks targeting a cluster. """

    # pylint: disable=too-many-arguments
    def __init__(self, playbooks_dir, cluster_id=None, log_dir=None, inventory=None, openshift_ansible=False, env=None):
        """ init the playbook executor """

        self.playbooks_dir = playbooks_dir
        self.cluster_id = cluster_id
        self.openshift_ansible = openshift_ansible
        self.log_dir = log_dir
        self.inventory = inventory
        self.env = env

        # This sets up the openshift ansible env
        if openshift_ansible:
            self.osa_inventory_env = None
            self.init_osa_env()

    def __call__(self, playbook, extra_vars=None, time=False, env=None):
        """ Execute the playbook with specified arguments. """

        extra_vars = extra_vars or {}
        playbook_path = os.path.join(self.playbooks_dir, playbook)

        # take care of the env
        pb_env = dict(os.environ)
        if self.env is not None:
            pb_env.update(self.env)

        if env is not None:
            pb_env.update(env)

        cmd = []
        if time:
            cmd += ['/usr/bin/time', '-p']

        cmd += ['/usr/bin/ansible-playbook']

        if self.inventory is not None:
            cmd += ['-i', self.inventory]

        if self.openshift_ansible:
            pb_env.update(self.osa_inventory_env)

            self.write_debug_inventory(playbook.replace('/', '_'), pb_env)
        else:
            if self.cluster_id:
                cmd += ['-e', 'cli_clusterid=' + self.cluster_id]

        for i in extra_vars.iteritems():
            cmd += ['-e', '='.join(i)]

        cmd.append(playbook_path)

        # TODO force for all jobs?
        pb_env['ANSIBLE_FORCE_COLOR'] = 'true'

        PlaybookExecutor.print_cmd(cmd, pb_env)

        # TODO cwd?
        subprocess.check_call(cmd, env=pb_env)

    def init_osa_env(self):
        """ init the openshift ansbile environment """

        self.osa_inventory_env = {"OO_INV_CLUSTERNAME" : self.cluster_id}

        ansible_env_plugin_dict = {'filter_plugins' : 'ANSIBLE_FILTER_PLUGINS',
                                   'lookup_plugins' : 'ANSIBLE_LOOKUP_PLUGINS',
                                   'callback_plugins' : 'ANSIBLE_CALLBACK_PLUGINS',
                                   'action_plugins' : 'ANSIBLE_ACTION_PLUGINS',
                                   'library' : 'ANSIBLE_LIBRARY',
                                  }

        ansible_valid_plugin_dirs = {d:[] for d in ansible_env_plugin_dict.keys()}
        ansible_plugin_paths = [self.playbooks_dir, self.playbooks_dir + '/roles/lib_utils',
                                self.playbooks_dir + '/roles/lib_openshift']

        for path in ansible_plugin_paths:
            for plugin_type in ansible_env_plugin_dict:
                plugin_path = os.path.join(path, plugin_type)
                if os.path.isdir(plugin_path):
                    ansible_valid_plugin_dirs[plugin_type].append(plugin_path)

        # Build the ENV vars
        for plugin, pdirs in ansible_valid_plugin_dirs.iteritems():
            if pdirs:
                self.osa_inventory_env[ansible_env_plugin_dict[plugin]] = ":".join(pdirs)

    def write_debug_inventory(self, playbook, env):
        """  Write the inventory out to a location for further debugging """

        if os.path.isdir(self.log_dir):
            inv_cmd = [self.inventory, '-y']
            now = datetime.datetime.now()
            now_str = now.strftime('%Y-%m-%d:%H:%M')

            log_file = os.path.join(self.log_dir, 'cicd_inventory.' + self.cluster_id + '.' + playbook + '.' + now_str)

            _ = PlaybookExecutor.run_cmd(inv_cmd, log_file, env=env)

    @staticmethod
    def run_cmd(cmd, logfile_path=None, stdin=None, env=None):
        """ run a command and return output and return code """

        proc_env = dict(os.environ)

        if env:
            proc_env.update(env)

        if logfile_path is not None:
            logfile = open(logfile_path, "w+")
            sout = logfile
            serr = subprocess.STDOUT
        else:
            logfile = None
            sout = subprocess.PIPE
            serr = subprocess.PIPE

        proc = subprocess.Popen(cmd, stdin=stdin, stdout=sout, stderr=serr, env=proc_env)
        stdout, stderr = proc.communicate()

        if logfile_path is not None:
            logfile.close()

        return proc.returncode, stdout, stderr

    @staticmethod
    def print_cmd(cmd, env):
        """ print the cmd and env so we can see what's running """

        print()
        print("ANSIBLE PLAYBOOK COMMAND: {}".format(" ".join(cmd)))
        print()
        print("ANSIBLE PLAYBOOK ENV VARS:")
        print("============================================")
        for key in env:
            if key.startswith("OO_INV") or key.startswith('ANSIBLE'):
                print("{}: {}".format(key, env[key]))
        print()
