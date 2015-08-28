#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

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
import sys
from openshift_tools.monitoring.zagg_sender import ZaggSender

class OpenShiftOC(object):
    ''' Class to wrap the oc command line tools
    '''
    @staticmethod
    def get_pod(pod_name, verbose=False):
        '''return a pod by name
        '''
        pods = OpenShiftOC.get_pods(verbose=verbose)
        regex = re.compile('%s-[0-9]-[a-z0-9]{5}$' % pod_name)
        for pod in pods['items']:
            results = regex.search(pod['metadata']['name'])
            if results:
                return pod

        return None

    @staticmethod
    def get_pods(pod_name='', verbose=False):
        '''return all pods
        '''
        cmd = ['get', 'pods', '--no-headers', '-o', 'json']
        if pod_name:
            cmd = ['get', 'pods', '--no-headers', pod_name, '-o', 'json']
        return json.loads(OpenShiftOC.oc_cmd(cmd, verbose))

    @staticmethod
    def new_app(path, verbose=False):
        '''run new-app
        '''
        cmd = ['new-app', path]
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
        cmd = ['new-project', name]
        return OpenShiftOC.oc_cmd(cmd, verbose)

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
    def oc_cmd(cmd, verbose=False):
        '''Base command for oc
        '''
        cmds = ['/usr/bin/oc']
        cmds.extend(cmd)
        if verbose:
            print ' '.join(cmds)
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': '/etc/openshift/master/admin.kubeconfig'})
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
    return urllib.urlopen('http://%s:%s' % (ip_addr, port)).read()

def main():
    ''' Do the application creation
    '''
    proj_name = 'ops-monitor'
    app = 'openshift/hello-openshift'
    verbose = False

    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        verbose = True

    start_time = time.time()
    if proj_name in  OpenShiftOC.get_projects(verbose):
        OpenShiftOC.delete_project(proj_name, verbose)

    OpenShiftOC.new_project(proj_name, verbose)

    OpenShiftOC.new_app(app, verbose)

    create_app = 1
    # Now we wait until the pod comes up
    for _ in range(24):
        time.sleep(5)
        pod = OpenShiftOC.get_pod('hello-openshift', verbose)
        if pod and pod['status']:
            if verbose:
                print pod['status']['phase']
        if pod and pod['status']['phase'] == 'Running' and pod['status'].has_key('podIP'):
            #c_results = curl(pod['status']['podIP'], '8080')
            #if c_results == 'Hello OpenShift!\n':
            if verbose:
                print 'success'
                print 'Time: %s' % str(time.time() - start_time)
            create_app = 0
            break

    else:
        if verbose:
            print 'Time: %s' % str(time.time() - start_time)
            print 'fail'

    zgs = ZaggSender()
    zgs.add_zabbix_keys({'create_app': create_app})
    zgs.send_metrics()


if __name__ == "__main__":
    main()

