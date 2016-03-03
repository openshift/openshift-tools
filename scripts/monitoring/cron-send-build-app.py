#!/usr/bin/env python
'''
    Quick and dirty create application check for v3
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name
# the to-many-branches

import subprocess
import json
import time
import re
import urllib
#import sys
import os

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

class OpenShiftOC(object):
    ''' Class to wrap the oc command line tools
    '''
    @staticmethod
    def get_pod(pod_name, proj_name, verbose=False):
        '''return a pod by name
        '''
        pods = OpenShiftOC.get_pods(proj_name=proj_name, verbose=verbose)
        #get pod except the build pod
        regex = re.compile('%s-[0-9]-(?!build)[a-z0-9]{5}$' % pod_name)
        for pod in pods['items']:
            results = regex.search(pod['metadata']['name'])
            if results:
                if verbose:
                    print 'find normal pod'
                return pod

        return None

    @staticmethod
    def get_build_pod(pod_name, proj_name, verbose=False):
        '''return a pod by name
        '''
        pods = OpenShiftOC.get_pods(proj_name=proj_name, verbose=verbose)
        #get the build pod
        regex = re.compile('%s-[0-9]-build' % pod_name)
        for pod in pods['items']:
            results = regex.search(pod['metadata']['name'])
            if results:
                if verbose:
                    print 'find build pod'
                return pod

        return None


    @staticmethod
    def get_pods(pod_name='', proj_name='', verbose=False):
        '''return all pods
        '''
        cmd = ['get', 'pods', '--no-headers', '-o', 'json']
        if pod_name:
            cmd = ['get', 'pods', '--no-headers', pod_name, '-o', 'json']

        if proj_name:
            cmd.append('-n%s'%proj_name)

        return json.loads(OpenShiftOC.oc_cmd(cmd, verbose))

    @staticmethod
    def new_app(path, proj_name, verbose=False):
        '''run new-app
        '''
        cmd = ['new-app', path, '-n', proj_name]
        return OpenShiftOC.oc_cmd(cmd, verbose)

    @staticmethod
    def delete_project(name, verbose=False):
        '''delete project
        '''
        cmd = ['delete', 'project', name]
        results = OpenShiftOC.oc_cmd(cmd, verbose)
        time.sleep(5)
        return results

    @staticmethod
    def new_project(name, verbose=False):
        '''create new project
        '''
        cmd = ['project']
        results = OpenShiftOC.oc_cmd(cmd, verbose)
        curr_project = results.split()[2].strip('"')
        cmd = ['new-project', name]
        rval = OpenShiftOC.oc_cmd(cmd, verbose)
        cmd = ['project', curr_project]
        results = OpenShiftOC.oc_cmd(cmd, verbose)
        return rval

    @staticmethod
    def get_projects(verbose=False):
        '''get all projects
        '''
        cmd = ['get', 'projects', '--no-headers']
        results = [proj.split()[0] for proj in OpenShiftOC.oc_cmd(cmd).split('\n') if proj and len(proj) > 0]
        if verbose:
            print results

        return results

    @staticmethod
    def get_route(proj_name='', verbose=False):
        '''return all the route
        '''
        cmd = ['get', 'route', '--no-headers', '-o', 'json']
        if proj_name:
            cmd.append('-n%s'%proj_name)
        return json.loads(OpenShiftOC.oc_cmd(cmd, verbose))

    @staticmethod
    def oc_cmd(cmd, verbose=False):
        '''Base command for oc
        '''
        cmds = ['/usr/bin/oc']
        cmds.extend(cmd)
        if verbose:
            print ' '.join(cmds)
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': '/etc/origin/master/admin.kubeconfig'})
        proc.wait()
        if proc.returncode == 0:
            output = proc.stdout.read()
            if verbose:
                print output
                print
            return output

        return "Error: %s.  Return: %s" % (proc.returncode, proc.stderr.read())


def curl(ip_addr, port):
    ''' Open an http connection to the url and read
    '''
    return urllib.urlopen('http://%s:%s' % (ip_addr, port)).code

def check_route(app, proj_name='', verbose=False):
    ''' after the pod been deployed ,check the route if get 200
    '''
    pod = OpenShiftOC.get_pod(app, proj_name, verbose)
    create_app_func = 1
    if pod and pod['status']['phase'] == 'Running' and pod['status'].has_key('podIP'):
        myroute = OpenShiftOC.get_route(proj_name, verbose)
        if myroute:
            hostip = myroute["items"][0]["spec"]["host"]
            httpstatus = curl(hostip, 80)
            if verbose:
                print 'The route is : %s' % myroute["items"][0]["spec"]["host"]
                print 'The httpstatus of route is : %s' % httpstatus
            if httpstatus == 200:
                create_app_func = 0
    return create_app_func

def main():
    ''' Do the application creation
    '''
    proj_name = 'ops-monitor-appbuild' + os.environ['ZAGG_CLIENT_HOSTNAME']
    app = 'nodejs-example'
    verbose = True

    start_time = time.time()
    if proj_name in  OpenShiftOC.get_projects(verbose):
        OpenShiftOC.delete_project(proj_name, verbose)

    OpenShiftOC.new_project(proj_name, verbose)

    OpenShiftOC.new_app(app, proj_name, verbose)
    #1 is error
    create_app = 1
    BuildTime = 0
    CreateTime = 0
    # Now we wait until the pod comes up
    for _ in range(24):
        time.sleep(10)
        #checking the building pod
        buildPod = OpenShiftOC.get_build_pod(app, proj_name, verbose)
        if buildPod and buildPod['status']['phase'] == 'Failed':
            BuildTime = time.time() - start_time
            print 'fail'
            break
        if buildPod and buildPod['status']['phase'] == 'Succeeded':
            BuildTime = time.time() - start_time
            for _ in range(24):
                time.sleep(5)
                create_app = check_route(app, proj_name, verbose)
                if create_app == 0:
                    CreateTime = time.time() - start_time
                    print 'success'
                    print 'Time: %s' % CreateTime
                    print 'BuildTime: %s' % BuildTime
                    break
            if create_app == 0:
                break
    else:
        BuildTime = time.time() - start_time
        print 'BuildTime: %s' % BuildTime
        print 'fail'
    if proj_name in  OpenShiftOC.get_projects(verbose):
        OpenShiftOC.delete_project(proj_name, verbose)

    zgs = ZaggSender()
    zgs.add_zabbix_keys({'openshift.master.app.build.create': create_app})
    zgs.add_zabbix_keys({'openshift.master.app.create.time': CreateTime})
    zgs.add_zabbix_keys({'openshift.master.app.build.time': BuildTime})
    zgs.send_metrics()


if __name__ == "__main__":
    main()

