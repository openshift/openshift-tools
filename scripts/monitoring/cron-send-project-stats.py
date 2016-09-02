#!/usr/bin/env python
'''
    Quick and dirty create application check for v3
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import subprocess
import json
import time
import re
import os
import atexit
import shutil
import string
import random
import argparse
import datetime
import sys

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

# pylint: disable=bare-except
def cleanup_file(inc_file):
    ''' clean up '''
    try:
        os.unlink(inc_file)
    except:
        pass

def copy_kubeconfig(config):
    ''' make a copy of the kubeconfig '''
    file_name = os.path.join('/tmp',
                             ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)))
    shutil.copy(config, file_name)
    atexit.register(cleanup_file, file_name)

    return file_name

class OpenShiftOC(object):
    ''' Class to wrap the oc command line tools '''
    def __init__(self, namespace, kubeconfig, args, verbose=False):
        ''' Constructor for OpenShiftOC '''
        self.namespace = namespace
        # used to delete the project ES index
        self.run_date = datetime.datetime.now().strftime("%Y.%m.%d")
        self.verbose = verbose
        self.kubeconfig = kubeconfig
        self.args = args

    def get_pod(self):
        '''return a pod by name'''
        pods = self.get_pods()
        podname = pod_name(self.args.name)
        # this will match on build pods but not deploy pods
        regex = re.compile('%s-[0-9]-[a-z0-9]{5}$' % podname)
        for pod in pods['items']:
            results = regex.search(pod['metadata']['name'])
            if results:
                # only report on running build pods, we'll wait if build pod is pending
                if "build" in pod['metadata']['name'] and pod['status']['phase'] != 'Running':
                    continue
                else: return pod

    def get_pods(self):
        '''return all pods '''
        cmd = ['get', 'pods', '--no-headers', '-o', 'json', '-n', self.namespace]
        results = self.oc_cmd(cmd)

        return json.loads(results)

    def new_app(self, path):
        '''run new-app '''
        cmd = ['new-app', path, '-n', self.namespace]
        return self.oc_cmd(cmd)

    def delete_project(self):
        '''delete project '''
        cmd = ['delete', 'project', self.namespace]
        results = self.oc_cmd(cmd)
        time.sleep(5)
        return results

    def new_project(self):
        '''create new project '''
        version = self.get_version()
        cmd = ['new-project', self.namespace]
        if "v3.2" in version:  ## remove this after BZ1333049 resolved in OSE
            rval = self.oadm_cmd(cmd)
        else:
            rval = self.oc_cmd(cmd)
        return rval

    def get_logs(self):
        '''get all pod logs'''
        pods = self.get_pods()
        result = ""
        for pod in pods['items']:
            result = result + self.oc_cmd(['logs', pod['metadata']['name'], '-n', self.namespace])

        if result == "":
            return 'Could not get logs for pod.  Could not determine pod name.'

        return result

    def get_route(self):
        '''get route to check if app is running'''
        cmd = ['get', 'route', '--no-headers', '-o', 'json', '-n', self.namespace]
        results = self.oc_cmd(cmd)
        return json.loads(results)

    def get_service(self):
        '''get service to check if app is running'''
        return json.loads(self.oc_cmd(['get', 'service', '--no-headers', '-n', self.namespace, '-o', 'json']))

    def get_events(self):
        '''get all events'''
        return self.oc_cmd(['get', 'events', '-n', self.namespace])


    def get_projects(self):
        '''get all projects '''
        cmd = ['get', 'projects', '--no-headers']
        results = [proj.split()[0] for proj in self.oc_cmd(cmd).split('\n') if proj and len(proj) > 0]

        return results

    def get_projects_json(self):
        '''get all project with json'''
        return json.loads(self.oc_cmd(['get', 'project', '--no-headers', '-o', 'json']))

    def get_version(self):
        '''get openshift version'''
        return self.oc_cmd(['version'])

    def oc_cmd(self, cmd):
        '''Base command for oc '''
        cmds = ['/usr/bin/oc']
        cmds.extend(cmd)
        print ' '.join(cmds)
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': self.kubeconfig, \
                                     'PATH': os.environ["PATH"]})
        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            if self.verbose:
                print "Stdout:"
                print stdout
                print "Stderr:"
                print stderr
            return stdout

        return "Error: %s.  Return: %s" % (proc.returncode, stderr)

    def oadm_cmd(self, cmd):
        '''Base command for oadm '''
        cmds = ['/usr/bin/oadm']
        cmds.extend(cmd)
        print ' '.join(cmds)
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': self.kubeconfig, \
                                     'PATH': os.environ["PATH"]})
        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            if self.verbose:
                print "Stdout:"
                print stdout
                print "Stderr:"
                print stderr
            return stdout

        return "Error: %s.  Return: %s" % (proc.returncode, stderr)
def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='OpenShift app create end-to-end test')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('--name', default="openshift/hello-openshift:v1.0.6", help='app template')
    return parser.parse_args()

def pod_name(name):
    """ strip pre/suffices from app name to get pod name """
    # for app deploy "https://github.com/openshift/hello-openshift:latest", pod name is hello-openshift
    if 'http' in name:
        name = name.rsplit('/')[-1]
    if 'git' in name:
        name = name.replace('.git', '')
    if '/' in name:
        name = name.split('/')[1]
    if ':' in name:
        name = name.split(':')[0]
    return name

def send_zagg_data(keep_time):
    ''' send data to Zagg'''
    zgs_time = time.time()
    zgs = ZaggSender()
    print "Send data to Zagg"
    zgs.add_zabbix_keys({'openshift.master.project.terminating.time': keep_time})
    try:
        zgs.send_metrics()
    except:
        print "Error sending to Zagg: %s \n %s " % sys.exc_info()[0], sys.exc_info()[1]
    print "Data sent in %s seconds" % str(time.time() - zgs_time)


def handle_fail(run_time, oocmd, pod):
    ''' Print failure info '''
    print 'Finished.'
    print 'State: Fail'
    print 'Time: %s' % run_time
    print 'Fetching Events:'
    oocmd.verbose = True
    print oocmd.get_events()
    print 'Fetching Logs:'
    print oocmd.get_logs()
    print 'Fetching Pod:'
    print pod

def main():
    ''' Do the application creation
    '''
    print '################################################################################'
    print '  Starting Checking project status - %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print '################################################################################'
    kubeconfig = copy_kubeconfig('/tmp/admin.kubeconfig')
    args = parse_args()
    namespace = 'ops-project-info-check'
    oocmd = OpenShiftOC(namespace, kubeconfig, args, verbose=False)

    projects_info = oocmd.get_projects_json()
    #deletionTimestamp
    print 'start checking'
    print 'current project number is %s' % len(projects_info['items'])
    time_keeps_max = 0
    try:
        for pro in projects_info['items']:
            #print pro['status']['phase']
            if 'Terminating' == pro['status']['phase']:
                print 'found it '
                print pro['metadata']['deletionTimestamp']
                temp_t = pro['metadata']['deletionTimestamp'].replace('T', ' ').replace('Z', '')
                old_time = datetime.datetime.strptime(temp_t, '%Y-%m-%d %H:%M:%S')
                #current_time = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                #current_time = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                current_time = datetime.datetime.now()
                time_keeps = current_time - old_time
                print 'the project in Terminating status for %s' % time_keeps

                time_keeps_max = max(time_keeps_max, (current_time - old_time).seconds)

                print time_keeps_max

    except ValueError, e:
        print 'something wrong when try to check the project one by one:', e

    send_zagg_data(time_keeps_max)
    print 'the logest Terminating project is there for %s seconds' % time_keeps_max

if __name__ == "__main__":
    main()
