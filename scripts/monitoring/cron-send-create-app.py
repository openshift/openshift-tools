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
from openshift_tools.monitoring.metric_sender import MetricSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ocutil = OCUtil()

commandDelay = 5 # seconds
# use parsed arg instead
#testLoopCountMax = 180 # * commandDelay = 15min
testCurlCountMax = 18 # * commandDelay = 1min30s
testNoPodCountMax = 18 # * commandDelay = 1min30s

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    ocy_time = time.time()
    ocy_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - ocy_time))
    return ocy_result

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift app create end-to-end test')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--source', default="openshift/hello-openshift:v1.0.6",
                        help='source application to use')
    parser.add_argument('--basename', default="test", help='base name, added to via openshift')
    parser.add_argument('--loopcount', default="36",
                        help="how many 5 second loops before giving up on app creation")
    return parser.parse_args()

def send_metrics(build_ran, create_app, route_http_failed, service_http_failed, run_time):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    if build_ran == 1:
        ms.add_metric({'openshift.master.app.build.create': create_app})
        ms.add_metric({'openshift.master.app.create.route_http_failed': route_http_failed})
        ms.add_metric({'openshift.master.app.create.service_http_failed': service_http_failed})
        ms.add_metric({'openshift.master.app.build.create.time': run_time})
    else:
        ms.add_metric({'openshift.master.app.create': create_app})
        ms.add_metric({'openshift.master.app.create.route_http_failed': route_http_failed})
        ms.add_metric({'openshift.master.app.create.service_http_failed': service_http_failed})
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
        logger.exception("Curl failed to connect to host")

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

    # Create a new project using 'oc' instead of 'oc adm'.
    # This will test the project-request template as part of project creation.
    # Skip writing to kubeconfig, since we don't need to keep a record of every project created.
    if not project:
        try:
            runOCcmd("new-project {} --skip-config-write=true".format(config.namespace), base_cmd='oc')
            time.sleep(commandDelay)
        except Exception:
            logger.exception('error creating new project')

    runOCcmd("new-app {} --name={} -n {}".format(
        config.source,
        config.podname,
        config.namespace,
    ))

    # Expose the service to test route creation.
    runOCcmd("expose svc {} -n {}".format(
        config.podname,
        config.namespace,
    ))


def testCurl(config):
    """ run curl and return service_http_code and route_http_code, have retries """
    logger.info('testCurl()')
    logger.debug(config)

    route_http_code = 0
    service_http_code = 0

    # attempt retries
    for curlCount in range(testCurlCountMax):
        # introduce small delay to give time for route to establish
        time.sleep(commandDelay)

        service = ocutil.get_service(config.podname)

        if service:
            logger.debug("service")
            logger.debug(service)

            service_http_code = curl(
                service['spec']['clusterIP'],
                service['spec']['ports'][0]['port']
             )

            logger.debug("service http code %s", service_http_code)

        route = ocutil.get_route(config.podname)

        if route:
            logger.debug("route")
            logger.debug(route)

            route_http_code = curl(
                route['spec']['host'],
                80
            )

            logger.debug("route http code %s", route_http_code)

        if route_http_code == 200 and service_http_code == 200:
            logger.debug("route and service curl completed in %d tries", curlCount)
            break

    return route_http_code, service_http_code


def test(config):
    """ run tests """
    logger.info('test()')
    logger.debug(config)

    build_ran = 0
    pod = None
    noPodCount = 0
    route_http_code = 0
    service_http_code = 0
    # assume these have failed, until we see a success.
    route_http_failed = 1
    service_http_failed = 1

    for _ in range(int(config.loopcount)):
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

            route_http_code, service_http_code = testCurl(config)

            # For the purpose of Zabbix alerting, it's easiest to do a
            # pass/fail numeric value here. This helps when totaling
            # the number of failures per hour.
            if route_http_code == 200:
              route_http_failed = 0
            if service_http_code == 200:
              service_http_failed = 0

            return {
                'build_ran': build_ran,
                'create_app': 0, # app create succeeded
                'route_http_code': route_http_code,
                'service_http_code': service_http_code,
                'route_http_failed': route_http_failed,
                'service_http_failed': service_http_failed,
                # route/service curl failures are reported independently of app-create now
                'failed': False,
                'pod': pod,
            }

    if build_ran:
        logger.critical("build timed out, please check build log for last messages")
    else:
        logger.critical("app create timed out, please check event log for information")

    return {
        'build_ran': build_ran,
        'create_app': 1, # app create failed
        'route_http_code': route_http_code,
        'service_http_code': service_http_code,
        'route_http_failed': route_http_failed,
        'service_http_failed': service_http_failed,
        'failed': True,
        'pod': pod,
    }

def teardown(config):
    """ clean up after testing """
    logger.info('teardown()')
    logger.debug(config)

    time.sleep(commandDelay)

    runOCcmd("delete project {}".format(
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

    ############# generate unique podname and namespace #############
    args.uid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
    args.timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    args.podname = '-'.join([args.basename, args.timestamp, args.uid]).lower()
    args.namespace = '-'.join(["sre-app-check", args.timestamp, args.uid]).lower()

    # This number is based on a few different facts:
    # 1. The FQDN for a route must be no longer than 63 characters.
    # 2. Namespaces must be no longer than 63 characters.
    # 3. Pod names must be no longer than 58 characters.
    if len(args.podname) > 24:
        raise ValueError("len(args.podname) cannot exceed 24, currently {}: {}".format(
            len(args.podname), args.podname
        ))

    ocutil.namespace = args.namespace
    ############# setup() #############
    try:
        setup(args)
    except Exception as e:
        logger.exception("error during setup()")
        exception = e

    ############# test() #############
    if not exception:
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
                'service_http_code': service_http_code,
                'route_http_code': route_http_code,
                'route_http_failed': route_http_failed,
                'service_http_failed': service_http_failed,
                'failed': True,
                'pod': None,
            }

        # finish time tracking
        run_time = str(time.time() - start_time)
        logger.info('Test finished. Time to complete test only: %s', run_time)

        ############# send data to zabbix #############
        try:
            send_metrics(
                test_response['build_ran'],
                test_response['create_app'],
                test_response['service_http_failed'],
                test_response['route_http_failed'],
                run_time
            )
        except Exception as e:
            logger.exception("error sending zabbix data")
            exception = e

        ############# collect more information if failed #############
        if test_response['failed']:
            try:
                ocutil.verbose = True
                logger.setLevel(logging.DEBUG)

                if test_response['pod']:
                    logger.info('Fetching Pod:')
                    logger.info(test_response['pod'])
                    logger.info('Fetching Logs: showing last 20, see file for full data')
                    logs = ocutil.get_log(test_response['pod']['metadata']['name'])
                    writeTmpFile(logs, filename=args.podname+".logs")
                    logger.info("\n".join(
                        logs.split("\n")[-20:]
                    ))
                logger.info('Fetching Events: see file for full data')
                events = "\n".join(
                    [event for event in runOCcmd('get events').split("\n") if args.podname in event]
                )
                writeTmpFile(events, filename=args.podname+".events")
                logger.info(events)
                # During a failure, this summary at the end of the script run makes it easy to tell what went wrong.
                logger.critical('Deploy State: Fail')
                if test_response['service_http_failed']:
                  logger.critical('Service HTTP response code: %s', test_response['service_http_code'])
                else:
                  logger.info('Service HTTP response code: %s', test_response['service_http_code'])

                if test_response['route_http_failed']:
                  logger.critical('Route HTTP response code: %s', test_response['route_http_code'])
                else:
                  logger.info('Route HTTP response code: %s', test_response['route_http_code'])

            except Exception as e:
                logger.exception("problem fetching additional error data")
                exception = e
        else:
            logger.info('Deploy State: Success')
            logger.info('Service HTTP response code: %s', test_response['service_http_code'])
            logger.info('Route HTTP response code: %s', test_response['route_http_code'])

    ############# teardown #############
    teardown(args)

    ############# raise any exceptions discovered #############
    if exception:
        raise exception

if __name__ == "__main__":
    main()
