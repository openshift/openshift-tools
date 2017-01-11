#!/usr/bin/env python
""" Report the usage of the pv """

# We just want to see any exception that happens
# don't want the script to die under any cicumstances
# script must try to clean itself up
# pylint: disable=broad-except

# main() function has a lot of setup and error handling
# pylint: disable=too-many-statements

# main() function raises a captured exception if there is one
# pylint: disable=raising-bad-type

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import argparse
import datetime
import random
import string
import time
import urllib2
import re

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ocutil = OCUtil()



def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    return ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    return ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift app create end-to-end test')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--source', default="openshift/hello-openshift:v1.0.6",
                        help='source application to use')
    parser.add_argument('--basename', default="test", help='base name, added to via openshift')
    parser.add_argument('--namespace', default="ops-health-monitoring",
                        help='namespace (be careful of using existing namespaces)')
    return parser.parse_args()

def send_metrics(build_ran, create_app, http_code, run_time):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    if build_ran == 1:
        ms.add_metric({'openshift.master.app.build.create': create_app})
        ms.add_metric({'openshift.master.app.build.create.code': http_code})
        ms.add_metric({'openshift.master.app.build.create.time': run_time})
    else:
        ms.add_metric({'openshift.master.app.create': create_app})
        ms.add_metric({'openshift.master.app.create.code': http_code})
        ms.add_metric({'openshift.master.app.create.time': run_time})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def writeTmpFile(data, filename=None, outdir="/tmp"):
    """ write string to file """
    filename = ''.join([
        outdir, '/',
        filename,
    ])

    with open(filename, 'w') as f:
        f.write(data)

    logger.info("wrote file: %s", filename)

def curl(ip_addr, port, timeout=30):
    """ Open an http connection to the url and read """
    url = 'http://%s:%s' % (ip_addr, port)
    logger.debug("curl(%s timeout=%ss)", url, timeout)

    try:
        return urllib2.urlopen(url, timeout=timeout).getcode()
    except urllib2.HTTPError, e:
        return e.fp.getcode()
    except Exception as e:
        logger.exception("Unknown error")

    return 0

def getPodStatus(pod):
    """ get pod status for display """
    #logger.debug("getPodStatus()")
    if not pod:
        return "no pod"

    if not pod['status']:
        return "no pod status"

    return "%s %s" % (pod['metadata']['name'], pod['status']['phase'])

def getPod(name):
    """ get Pod from all possible pods """
    pods = ocutil.get_pods()
    result = None

    for pod in pods['items']:
        if pod and pod['metadata']['name'] and pod['metadata']['name'].startswith(name):
            # if we have a pod already, and this one is a build or deploy pod, don't worry about it
            # we want podname-xyz12 to be priority
            # if we dont already have a pod, then this one will do
            if result:
                if pod['metadata']['name'].endswith("build"):
                    continue

                if pod['metadata']['name'].endswith("deploy"):
                    continue

            result = pod

    return result

def setup(config):
    """ global setup for tests """
    logger.info('setup()')
    logger.debug(config)

    project = None

    try:
        project = runOCcmd_yaml("get project {}".format(config.namespace))
        logger.debug(project)
    except Exception:
        pass # don't want exception if project not found

    if not project:
        try:
            runOCcmd("new-project {}".format(config.namespace), base_cmd='oadm')
            time.sleep(commandDelay)
        except Exception:
            logger.exception('error creating new project')

    runOCcmd("new-app {} --name={} -n {}".format(
        config.source,
        config.podname,
        config.namespace,
    ))

def testCurl(config):
    """ run curl and return http_code, have retries """
    logger.info('testCurl()')
    logger.debug(config)

    http_code = 0

    # attempt retries
    for curlCount in range(testCurlCountMax):
        # introduce small delay to give time for route to establish
        time.sleep(commandDelay)

        service = ocutil.get_service(config.podname)

        if service:
            logger.debug("service")
            logger.debug(service)

            http_code = curl(
                service['spec']['clusterIP'],
                service['spec']['ports'][0]['port']
            )

            logger.debug("http code %s", http_code)

        if http_code == 200:
            logger.debug("curl completed in %d tries", curlCount)
            break

    return http_code


def test(config):
    """ run tests """
    logger.info('test()')
    logger.debug(config)

    build_ran = 0
    pod = None
    noPodCount = 0
    http_code = 0

    for _ in range(testLoopCountMax):
        time.sleep(commandDelay)
        pod = getPod(config.podname)

        if not pod:
            noPodCount = noPodCount + 1
            if noPodCount > testNoPodCountMax:
                logger.critical("cannot find pod, fail early")
                break

            logger.debug("cannot find pod")
            continue # cannot test pod further

        noPodCount = 0

        if not pod['status']:
            logger.error("no pod status")
            continue # cannot test pod further

        logger.info(getPodStatus(pod))

        if pod['status']['phase']:
            if pod['status']['phase'] == "Failed":
                logger.error("Pod Failed")
                break

            if pod['status']['phase'] == "Error":
                logger.error("Pod Error")
                break

        if pod['metadata']['name'].endswith("build"):
            build_ran = 1
            continue

        if pod['metadata']['name'].endswith("deploy"):
            continue

        if pod['status']['phase'] == 'Running' \
            and pod['status'].has_key('podIP') \
            and not pod['metadata']['name'].endswith("build"):

            http_code = testCurl(config)

            return {
                'build_ran': build_ran,
                'create_app': 0, # app create succeeded
                'http_code': http_code,
                'failed': (http_code != 200), # must be 200 to succeed
                'pod': pod,
            }

    if build_ran:
        logger.critical("build timed out, please check build log for last messages")
    else:
        logger.critical("app create timed out, please check event log for information")

    return {
        'build_ran': build_ran,
        'create_app': 1, # app create failed
        'http_code': http_code,
        'failed': True,
        'pod': pod,
    }

def teardown(config):
    """ clean up after testing """
    logger.info('teardown()')
    logger.debug(config)

    time.sleep(commandDelay)

    runOCcmd("delete all -l app={} -n {}".format(
        config.podname,
        config.namespace,
    ))

def get_dynamic_pod_name():
    """get the max_capacity of the cluster"""
    pods = ocutil.get_pods()
    dynamic_pod_name = ""
    pattern = re.compile(r'online-volume-provisioner-') 
    for pod in pods['items']:
        pod_name = pod['metadata']['name']
        match = pattern.search(pod_name)
        #find the dynamic pod name
        if match:
            dynamic_pod_name = pod_name
    return dynamic_pod_name

def get_max_capacity(pod_name):
    """get the env from the dynamic pod """
    env_info = runOCcmd_yaml(" env pod/"+pod_name)

    envs = env_info['spec']['containers']
    max_capacity = 0
    for en in envs[0]['env']:
        print en['name']
        if en['name'] == 'MAXIMUM_CLUSTER_CAPACITY':
            max_capacity = en['value']
    return max_capacity





def main():
    """ report pv usage  """
    exception = None

    logger.info('################################################################################')
    logger.info('  Starting Report pv usage - %s', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info('################################################################################')
    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ocutil.namespace = "openshift-infra"

    dynamic_pod_name = get_dynamic_pod_name()

    print 'the pod name is :',dynamic_pod_name
    
    if dynamic_pod_name == "":
        #means this cluster have no dynamic pv 
        pass
    else:
        MAXIMUM_CLUSTER_CAPACITY = get_max_capacity(dynamic_pod_name)
        print MAXIMUM_CLUSTER_CAPACITY


if __name__ == "__main__":
    main()
