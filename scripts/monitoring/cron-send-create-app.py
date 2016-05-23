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
import urllib
import os
import atexit
import shutil
import string
import random

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
    def __init__(self, namespace, pod_name, kubeconfig, verbose=False):
        ''' Constructor for OpenShiftOC '''
        self.namespace = namespace
        self.pod_name = pod_name
        self.verbose = verbose
        self.kubeconfig = kubeconfig

    def get_pod(self):
        '''return a pod by name '''
        pods = self.get_pods()
        regex = re.compile('%s-[0-9]-[a-z0-9]{5}$' % self.pod_name)
        for pod in pods['items']:
            results = regex.search(pod['metadata']['name'])
            if results:
                return pod

        return None

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
        cmd = ['project']
        results = self.oc_cmd(cmd)
        curr_project = results.split()[2].strip('"')
        version = self.get_version()
        cmd = ['new-project', self.namespace]
        if "v3.2" in version:  ## remove this after BZ1333049 resolved in OSE
            rval = self.oadm_cmd(cmd)
        else:
            rval = self.oc_cmd(cmd)
        cmd = ['project', curr_project]
        results = self.oc_cmd(cmd)
        return rval

    def get_logs(self):
        '''get all events'''
        pod = self.get_pod()
        if pod:
            return self.oc_cmd(['logs', pod['metadata']['name'], '-n', self.namespace])

        return 'Could not get logs for pod.  Could not determine pod name.'

    def get_events(self):
        '''get all events'''
        return self.oc_cmd(['get', 'events', '-n', self.namespace])


    def get_projects(self):
        '''get all projects '''
        cmd = ['get', 'projects', '--no-headers']
        results = [proj.split()[0] for proj in self.oc_cmd(cmd).split('\n') if proj and len(proj) > 0]

        return results

    def get_version(self):
        '''get openshift version'''
        return self.oc_cmd(['version'])

    def oc_cmd(self, cmd):
        '''Base command for oc '''
        cmds = ['/usr/bin/oc']
        cmds.extend(cmd)
        print ' '.join(cmds)
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': self.kubeconfig})
        proc.wait()
        if proc.returncode == 0:
            output = proc.stdout.read()
            if self.verbose:
                print "Stdout:"
                print output
                print "Stderr:"
                print proc.stderr.read()
            return output

        return "Error: %s.  Return: %s" % (proc.returncode, proc.stderr.read())

    def oadm_cmd(self, cmd):
        '''Base command for oadm '''
        cmds = ['/usr/bin/oadm']
        cmds.extend(cmd)
        print ' '.join(cmds)
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': self.kubeconfig})
        proc.wait()
        if proc.returncode == 0:
            output = proc.stdout.read()
            if self.verbose:
                print "Stdout:"
                print output
                print "Stderr:"
                print proc.stderr.read()
            return output

        return "Error: %s.  Return: %s" % (proc.returncode, proc.stderr.read())


def curl(ip_addr, port):
    ''' Open an http connection to the url and read
    '''
    return urllib.urlopen('http://%s:%s' % (ip_addr, port)).read()

def main():
    ''' Do the application creation
    '''
    print '################################################################################'
    print '  Starting App Create'
    print '################################################################################'
    kubeconfig = copy_kubeconfig('/tmp/admin.kubeconfig')
    namespace = 'ops-monitor-' + os.environ['ZAGG_CLIENT_HOSTNAME']
    oocmd = OpenShiftOC(namespace, 'hello-openshift', kubeconfig, verbose=False)
    app = 'openshift/hello-openshift:v1.0.6'

    start_time = time.time()
    if namespace in  oocmd.get_projects():
        oocmd.delete_project()

    oocmd.new_project()

    oocmd.new_app(app)

    create_app = 1
    pod = None
    # Now we wait until the pod comes up
    for _ in range(24):
        time.sleep(5)
        pod = oocmd.get_pod()
        if pod and pod['status']:
            print 'Polling Pod status: %s' % pod['status']['phase']
        if pod and pod['status']['phase'] == 'Running' and pod['status'].has_key('podIP'):
            #c_results = curl(pod['status']['podIP'], '8080')
            #if c_results == 'Hello OpenShift!\n':
            print 'Finished.'
            print 'State: Success'
            print 'Time: %s' % str(time.time() - start_time)
            create_app = 0
            break

    else:
        print 'Finished.'
        print 'State: Fail'
        print 'Time: %s' % str(time.time() - start_time)
        print 'Fetching Events:'
        oocmd.verbose = True
        print oocmd.get_events()
        print 'Fetching Logs:'
        print oocmd.get_logs()
        print 'Fetching Pod:'
        print pod

    if namespace in oocmd.get_projects():
        oocmd.delete_project()

    zgs = ZaggSender()
    zgs.add_zabbix_keys({'openshift.master.app.create': create_app})
    zgs.send_metrics()


if __name__ == "__main__":
    main()
