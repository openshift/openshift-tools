#!/usr/bin/env python
""" Create application check for v3 """

# We just want to see any exception that happens
# don't want the script to die under any cicumstances
# script must try to clean itself up
# pylint: disable=broad-except

# main() function has a lot of setup and error handling
# pylint: disable=too-many-statements

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
import datetime
import sys

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# pylint: disable=bare-except
def cleanup_file(inc_file):
    """ clean up """
    try:
        os.unlink(inc_file)
    except:
        pass

def copy_kubeconfig(config):
    """ make a copy of the kubeconfig """
    file_name = os.path.join('/tmp', ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(7)
    ))
    shutil.copy(config, file_name)
    atexit.register(cleanup_file, file_name)

    return file_name

class OpenShiftOC(object):
    """ Class to wrap the oc command line tools """
    def __init__(self, namespace, kubeconfig, args, verbose=False):
        """ Constructor for OpenShiftOC """
        self.namespace = namespace
        # used to delete the project ES index
        self.run_date = datetime.datetime.now().strftime("%Y.%m.%d")
        self.verbose = verbose
        self.kubeconfig = kubeconfig
        self.args = args

    def get_pod(self):
        """return a pod by name"""
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
        """return all pods """
        cmd = ['get', 'pods', '--no-headers', '-o', 'json', '-n', self.namespace]
        results = self.oc_cmd(cmd)

        return json.loads(results)

    def new_app(self, path):
        """run new-app """
        cmd = ['new-app', path, '-n', self.namespace]
        return self.oc_cmd(cmd)

    def delete_project(self):
        """delete project """
        cmd = ['delete', 'project', self.namespace]
        results = self.oc_cmd(cmd)
        time.sleep(5)
        return results

    def new_project(self):
        """create new project """
        version = self.get_version()
        cmd = ['new-project', self.namespace]
        if "v3.2" in version:  ## remove this after BZ1333049 resolved in OSE
            rval = self.oadm_cmd(cmd)
        else:
            rval = self.oc_cmd(cmd)
        return rval

    def get_logs(self):
        """get all pod logs"""
        pods = self.get_pods()
        result = ""
        for pod in pods['items']:
            result = result + self.oc_cmd(['logs', pod['metadata']['name'], '-n', self.namespace])

        if result == "":
            return 'Could not get logs for pod.  Could not determine pod name.'

        return result

    def get_route(self):
        """get route to check if app is running"""
        cmd = ['get', 'route', '--no-headers', '-o', 'json', '-n', self.namespace]
        results = self.oc_cmd(cmd)
        return json.loads(results)

    def get_service(self):
        """get service to check if app is running"""
        return json.loads(self.oc_cmd(
            ['get', 'service', '--no-headers', '-n', self.namespace, '-o', 'json']
        ))

    def get_events(self):
        """get all events"""
        return self.oc_cmd(['get', 'events', '-n', self.namespace])


    def get_projects(self):
        """get all projects """
        cmd = ['get', 'projects', '--no-headers']
        results = [
            proj.split()[0] for proj in self.oc_cmd(cmd).split('\n') if proj and len(proj) > 0
        ]

        return results

    def get_version(self):
        """get openshift version"""
        return self.oc_cmd(['version'])

    def oc_cmd(self, cmd):
        """Base command for oc """
        cmds = ['/usr/bin/oc']
        cmds.extend(cmd)
        logger.debug(' '.join(cmds))
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': self.kubeconfig, \
                                     'PATH': os.environ["PATH"]})
        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            if self.verbose:
                logger.debug("Stdout:")
                logger.debug(stdout)
                logger.debug("Stderr:")
                logger.debug(stderr)
            return stdout

        return "Error: %s.  Return: %s" % (proc.returncode, stderr)

    def oadm_cmd(self, cmd):
        """Base command for oadm """
        cmds = ['/usr/bin/oadm']
        cmds.extend(cmd)
        logger.debug(' '.join(cmds))
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                env={'KUBECONFIG': self.kubeconfig, \
                                     'PATH': os.environ["PATH"]})
        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            if self.verbose:
                logger.debug("Stdout:")
                logger.debug(stdout)
                logger.debug("Stderr:")
                logger.debug(stderr)
            return stdout

        return "Error: %s.  Return: %s" % (proc.returncode, stderr)

    def delete_es_index(self):
        """ delete elasticsearch index """
        # find project uuid
        get_project_uid_cmd = ['get', 'project', '-o', 'json', self.namespace]
        project = json.loads(self.oc_cmd(get_project_uid_cmd))
        if project:
            project_uid = project['metadata']['uid']
        else:
            logger.error("Failed finding project uid!")
            return 0
        # find logging pod
        get_log_pods_cmd = ['get', 'pods', '-o', 'json', '-n', 'logging']
        pods = json.loads(self.oc_cmd(get_log_pods_cmd))
        regex = re.compile('logging-es-*')
        for pod in pods['items']:
            pod_found = regex.search(pod['metadata']['name'])
            if pod_found:
                project_es_uuid = self.namespace + "." + project_uid + "." + self.run_date
                curl_cmd = ['curl', '-X', 'DELETE', \
                    '--key', '/etc/elasticsearch/keys/admin-key', \
                    '--cert', '/etc/elasticsearch/keys/admin-cert', \
                    '--cacert', '/etc/elasticsearch/keys/admin-ca', \
                    'https://localhost:9200/' + project_es_uuid]
                delete_cmd = ['exec', pod['metadata']['name'], '-n', 'logging', '--'] + curl_cmd
                delete_results = self.oc_cmd(delete_cmd)
                if self.verbose:
                    logger.debug(delete_results)
                return delete_results
        logger.error("Failed finding logging pod")
        return 0

def curl(ip_addr, port):
    """ Open an http connection to the url and read """
    logger.debug("curl()")

    code = 0
    timeout = 30 ## only wait this number of seconds for a response
    try:
        code = urllib2.urlopen( \
            'http://%s:%s' % (ip_addr, port), timeout=timeout).getcode()
    except urllib2.HTTPError, e:
        code = e.fp.getcode()
    except urllib2.URLError, e:
        logger.error(
            "timed out in %s seconds opening http://%s:%s",
            timeout, ip_addr, port
        )
    return code

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift app create end-to-end test')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--name', default="openshift/hello-openshift:v1.0.6", help='app template')
    parser.add_argument('--namespace', default="default", help='additional text for namespace')
    return parser.parse_args()

def pod_name(name):
    """ strip pre/suffices from app name to get pod name """
    logger.debug("pod_name()")

    # for app deploy "https://github.com/openshift/hello-openshift:latest",
    # pod name is hello-openshift
    if 'http' in name:
        name = name.rsplit('/')[-1]
    if 'git' in name:
        name = name.replace('.git', '')
    if '/' in name:
        name = name.split('/')[1]
    if ':' in name:
        name = name.split(':')[0]
    return name

def send_zagg_data(build_ran, create_app, http_code, run_time):
    """ send data to Zagg"""
    logger.debug("send_zagg_data()")

    zgs_time = time.time()
    zgs = ZaggSender()
    logger.info("Send data to Zagg")

    if build_ran == 1:
        zgs.add_zabbix_keys({'openshift.master.app.build.create': create_app})
        zgs.add_zabbix_keys({'openshift.master.app.build.create.code': http_code})
        zgs.add_zabbix_keys({'openshift.master.app.build.create.time': run_time})
    else:
        zgs.add_zabbix_keys({'openshift.master.app.create': create_app})
        zgs.add_zabbix_keys({'openshift.master.app.create.code': http_code})
        zgs.add_zabbix_keys({'openshift.master.app.create.time': run_time})

    try:
        zgs.send_metrics()
        logger.info("Data sent to Zagg in %s seconds", str(time.time() - zgs_time))
    except:
        logger.error("Error sending data to Zagg: %s \n %s ", sys.exc_info()[0], sys.exc_info()[1])

def getPodStatus(pod):
    """ get pod status for display """
    logger.debug("getPodStatus()")
    if not pod:
        return "no pod"

    if not pod['status']:
        return "no pod status"

    return "%s %s" % (pod['metadata']['name'], pod['status']['phase'])

def setup(config, oocmd=None,):
    """ global setup for tests """
    logger.info('setup()')
    oocmd.delete_project()
    time.sleep(5)
    oocmd.new_project()
    time.sleep(5)

    return config

def test(config, oocmd=None,):
    """ run tests """
    logger.info('test()')

    oocmd.new_app(config['applicationName'])

    build_ran = 0
    pod = None
    lastKnownPod = None
    http_code = 0

    # Now we wait until the pod comes up
    for loopCount in range(120):
        time.sleep(5)
        pod = oocmd.get_pod()

        if not pod:
            if not lastKnownPod and loopCount > 6:
                logger.critical("cannot find pod, fail early")
                break

            logger.debug("cannot find pod")
            continue # cannot test pod further

        lastKnownPod = pod

        if not pod['status']:
            logger.error("no pod status")
            continue # cannot test pod further

        logger.info(getPodStatus(pod))

        if pod['status'] and "build" in pod['metadata']['name']:
            build_ran = 1

        if pod['status']['phase'] == 'Running' \
            and pod['status'].has_key('podIP') \
            and not "build" in pod['metadata']['name']:

            # introduce small delay to give time for route to establish
            time.sleep(2)

            # test pods http capability
            route = oocmd.get_route()
            if route['items']:
                # FIXME: no port in the route object, is 80 a safe assumption?
                http_code = curl(route['items'][0]['spec']['host'], 80)
            else:
                service = oocmd.get_service()
                http_code = curl(service['items'][0]['spec']['clusterIP'], \
                    service['items'][0]['spec']['ports'][0]['port'])

            return {
                'build_ran': build_ran,
                'create_app': 0, # app create succeeded
                'http_code': http_code,
                'failed': (http_code != 200), # must be 200 to succeed
                'pod': pod,
            }

    return {
        'build_ran': build_ran,
        'create_app': 1, # app create failed
        'http_code': http_code,
        'failed': True,
        'pod': pod,
    }


def teardown(config, oocmd=None,):
    """ clean up after testing """
    logger.info('teardown()')

    try:
        oocmd.delete_es_index()
    except Exception as e:
        logger.exception('problem with delete_es_index')

    time.sleep(5)

    oocmd.delete_project()

    return config

def main():
    """ setup / test / teardown with exceptions to ensure teardown """

    logger.info('################################################################################')
    logger.info('  Starting App Create - %s', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info('################################################################################')
    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    kubeconfig = copy_kubeconfig('/tmp/admin.kubeconfig')
    namespace = '-'.join([
        'ops-health',
        args.namespace,
        pod_name(args.name),
        os.environ['ZAGG_CLIENT_HOSTNAME'],
    ])

    oocmd = OpenShiftOC(namespace, kubeconfig, args, verbose=False)

    config = {
        'args': args,
        'namespace': namespace,
        'applicationName': args.name,
    }

    # delete project, make new project
    setup(config, oocmd=oocmd,)

    # start time tracking
    start_time = time.time()

    # run tests, collect results
    try:
        test_response = test(config, oocmd=oocmd,)
    except Exception as e:
        logger.critical('problem running test')
        logger.critical(e)
        test_response = {
            'build_ran': 0,
            'create_app': 1, # app create failed
            'http_code': 0,
            'failed': True,
            'pod': None,
        }
    logger.debug("test_response")
    logger.debug(test_response)

    # finish time tracking
    run_time = str(time.time() - start_time)

    logger.info('Test finished. Time to complete test only: %s', run_time)

    # send data to zabbix
    try:
        send_zagg_data(
            test_response['build_ran'],
            test_response['create_app'],
            test_response['http_code'],
            run_time
        )
    except Exception as e:
        logger.critical('problem sending zabbix data')
        logger.critical(e)

    if test_response['failed']:
        try:
            oocmd.verbose = True
            logger.setLevel(logging.DEBUG)
            logger.critical('Deploy State: Fail')
            logger.info('Fetching Events:')
            logger.info(oocmd.get_events())
            logger.info('Fetching Logs:')
            logger.info(oocmd.get_logs())
            logger.info('Fetching Pod:')
            logger.info(test_response['pod'])
        except Exception as e:
            logger.critical('problem fetching additional error data')
            logger.critical(e)
    else:
        logger.info('Deploy State: Success')
        logger.info('Service HTTP response code: %s', test_response['http_code'])

    # cleanup project
    try:
        teardown(config, oocmd=oocmd,)
    except Exception as e:
        logger.critical('problem cleaning up project')
        logger.critical(e)

if __name__ == "__main__":
    main()
