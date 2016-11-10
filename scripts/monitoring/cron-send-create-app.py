#!/usr/bin/env python
""" Create application check for v3 """

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

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.zagg_sender import ZaggSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ocutil = OCUtil()

commandDelay = 5 # seconds

def runOCcmd(cmd):
    """ log commands through ocutil """
    logger.info("oc " + cmd)
    return ocutil.run_user_cmd(cmd)

def runOCcmd_yaml(cmd):
    """ log commands through ocutil """
    logger.info("oc " + cmd)
    return ocutil.run_user_cmd_yaml(cmd)

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

    zgs.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - zgs_time))

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
    logger.debug("getPodStatus()")
    if not pod:
        return "no pod"

    if not pod['status']:
        return "no pod status"

    return "%s %s" % (pod['metadata']['name'], pod['status']['phase'])

def getPod(name):
    """ get Pod from all possible pods """
    pods = ocutil.get_pods()
    for pod in pods['items']:
        if pod and pod['metadata']['name'] and pod['metadata']['name'].startswith(name):
            # only report on running build pods, we'll wait if build pod is pending
            if pod['metadata']['name'].endswith("build") and pod['status']['phase'] != 'Running':
                continue
            else:
                return pod

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
            runOCcmd("new-project {}".format(config.namespace))
            time.sleep(commandDelay)
        except Exception:
            logger.exception('error creating new project')

    runOCcmd("new-app {} --name={} -n {}".format(
        config.source,
        config.podname,
        config.namespace,
    ))

def test(config):
    """ run tests """
    logger.info('test()')
    logger.debug(config)

    build_ran = 0
    pod = None
    lastKnownPod = None
    http_code = 0

    for loopCount in range(120):
        time.sleep(commandDelay)
        pod = getPod(config.podname)

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

        if pod['status']['phase']:
            if pod['status']['phase'] == "Failed":
                logger.error("Error with pod")
                break

        if pod['status'] and pod['metadata']['name'].endswith("build"):
            build_ran = 1

        if pod['status']['phase'] == 'Running' \
            and pod['status'].has_key('podIP') \
            and not pod['metadata']['name'].endswith("build"):

            # attempt retries
            for curlCount in range(10):
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

def teardown(config):
    """ clean up after testing """
    logger.info('teardown()')
    logger.debug(config)

    time.sleep(commandDelay)

    runOCcmd("delete all -l app={} -n {}".format(
        config.podname,
        config.namespace,
    ))

def main():
    """ setup / test / teardown with exceptions to ensure teardown """
    exception = None

    logger.info('################################################################################')
    logger.info('  Starting App Create - %s', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info('################################################################################')
    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ocutil.namespace = args.namespace

    args.uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
    args.timestamp = datetime.datetime.utcnow().strftime("%m%d%H%Mz")
    args.podname = '-'.join([args.basename, args.timestamp, args.uid]).lower()

    if len(args.podname) > 24:
        raise ValueError("len(args.podname) cannot exceed 24, currently {}: {}".format(
            len(args.podname), args.podname
        ))

    setup(args)

    # start time tracking
    start_time = time.time()

    try:
        test_response = test(args)
        logger.debug(test_response)
    except Exception as e:
        logger.exception("error during test()")
        exception = e
        test_response = {
            'build_ran': 0,
            'create_app': 1, # app create failed
            'http_code': 0,
            'failed': True,
            'pod': None,
        }

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
        logger.exception("error sending zabbix data")
        exception = e

    if test_response['failed']:
        try:
            ocutil.verbose = True
            logger.setLevel(logging.DEBUG)
            logger.critical('Deploy State: Fail')
            logger.info('Fetching Pod:')
            logger.info(test_response['pod'])
            logger.info('Fetching Events:')
            logger.info(runOCcmd('get events'))
            if test_response['pod']:
                logger.info('Fetching Logs:')
                logger.info(ocutil.get_log(test_response['pod']['metadata']['name']))
        except Exception as e:
            logger.exception("problem fetching additional error data")
            exception = e
    else:
        logger.info('Deploy State: Success')
        logger.info('Service HTTP response code: %s', test_response['http_code'])

    teardown(args)

    if exception:
        raise exception

if __name__ == "__main__":
    main()
