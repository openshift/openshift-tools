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
import urllib2
import os
import atexit
import shutil
import string
import random
import argparse

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
    code = 0
    try:
        code = urllib2.urlopen('http://%s:%s' % (ip_addr, port)).getcode()
    except urllib2.HTTPError, e:
        code = e.fp.getcode()
    return code



def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='OpenShift app create end-to-end test')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('--name', default="openshift/hello-openshift", help='app template')
    return parser.parse_args()

def pod_name(name):
    """ strip pre/suffices from app name to get pod name """
    # for app deploy "openshift/hello-openshift:latest", pod name is hello-openshift
    if '/' in name:
        name = name.split('/')[1]
    if ':' in name:
        name = name.split(':')[0]
    return name


def send_zagg_data(build_ran, create_app, http_code, run_time):
    ''' send data to Zagg'''
    zgs = ZaggSender()
    print "Send data to Zagg"
    if build_ran == 1:
        zgs.add_zabbix_keys({'openshift.master.app.build.create': create_app})
        zgs.add_zabbix_keys({'openshift.master.app.build.create.code': http_code})
        zgs.add_zabbix_keys({'openshift.master.app.build.create.time': run_time})
    else:
        zgs.add_zabbix_keys({'openshift.master.app.create': create_app})
        zgs.add_zabbix_keys({'openshift.master.app.create.code': http_code})
        zgs.add_zabbix_keys({'openshift.master.app.create.time': run_time})
    zgs.send_metrics()

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
    print '  Starting App Create'
    print '################################################################################'
    kubeconfig = copy_kubeconfig('/tmp/admin.kubeconfig')
    args = parse_args()
    namespace = 'ops-' + pod_name(args.name) + '-' + os.environ['ZAGG_CLIENT_HOSTNAME']
    oocmd = OpenShiftOC(namespace, kubeconfig, args, verbose=False)
    app = args.name

    start_time = time.time()
    if namespace in  oocmd.get_projects():
        oocmd.delete_project()

    oocmd.new_project()

    oocmd.new_app(app)

    create_app = 1
    build_ran = 0
    pod = None
    http_code = 0
    run_time = 0

    # Now we wait until the pod comes up
    for _ in range(120):
        time.sleep(5)
        pod = oocmd.get_pod()
        if pod and pod['status'] and not "build" in pod['metadata']['name']:
            print 'Polling Pod status: %s' % pod['status']['phase']
        if pod and pod['status'] and "build" in pod['metadata']['name']:
            print 'Polling Build Pod status: %s' % pod['status']['phase']
            build_ran = 1
        if pod \
            and pod['status']['phase'] == 'Running' \
            and pod['status'].has_key('podIP') \
            and not "build" in pod['metadata']['name']:
            route = oocmd.get_route()
            if route['items']:
                # FIXME: no port in the route object, is 80 a safe assumption?
                http_code = curl(route['items'][0]['spec']['host'], 80)
            else:
                service = oocmd.get_service()
                http_code = curl(service['items'][0]['spec']['clusterIP'], \
                    service['items'][0]['spec']['ports'][0]['port'])
            print 'Finished.'
            print 'Deploy State: Success'
            print 'Service HTTP response code: %s' % http_code
            run_time = str(time.time() - start_time)
            print 'Time: %s' % run_time
            create_app = 0
            break

    else:
        run_time = str(time.time() - start_time)
        handle_fail(run_time, oocmd, pod)

    if namespace in oocmd.get_projects():
        oocmd.delete_project()

    send_zagg_data(build_ran, create_app, http_code, run_time)

if __name__ == "__main__":
    main()
