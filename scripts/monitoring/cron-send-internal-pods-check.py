#!/usr/bin/env python
''' Send Cluster Infra node's pod status to Zagg '''

# TODO: change to use arguments for podname, and run once per podname

#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=broad-except

import argparse
import logging

from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logging.getLogger().setLevel(logging.WARN)

class InfraNodePodStatus(object):
    '''
      This is a check for making sure the internal pods like
      router and registry running and located on different infra nodes
    '''
    def __init__(self, args=None, ):
        '''initial for the InfraNodePodStatus'''
        self.args = args
        self.kubeconfig = '/tmp/admin.kubeconfig'
        self.oc = OCUtil(namespace=self.args.namespace, config_file=self.kubeconfig)
        self.all_pods = self.get_all_pods()

    def get_all_pods(self):
        ''' get all the pod information '''
        pods = self.oc.get_pods()
        pod_report = {}
        for pod in pods['items']:
            pod_name = pod['metadata']['name']
            pod_report[pod_name] = {}
            pod_report[pod_name]['hostIP'] = pod['status']['hostIP']
            pod_report[pod_name]['status'] = pod['status']['phase']
        return pod_report

    def get_expected_replicas(self, deploymentconfig):
        ''' get expected replica count from deploymentconfig '''
        defined_replicas = self.oc.get_dc(deploymentconfig)['spec']['replicas']
        return defined_replicas

    def get_pods_by_name(self, podname):
        """get_pods_by_name"""
        return [self.all_pods[i] for i in self.all_pods.keys() if i.startswith(podname + '-')]

    def check_pods(self, podname, keybase="", pod_optional=False, ):
        ''' to compare the pod host ip and check the pod status '''
        logging.getLogger().info("Finding pods for: %s", podname)

        result_code = 1

        pods = self.get_pods_by_name(podname)
        logging.getLogger().info("Pods Found: %s", len(pods))

        expected_replicas = 0
        try:
            expected_replicas = self.get_expected_replicas(podname)
        except Exception:
            logging.getLogger().warn("dc not found for pod %s", podname)
            if pod_optional:
                logging.getLogger().warn(
                    "Some clusters don't have pod %s, please confirm before trying to fix this",
                    podname)
            return # nothing we should do, so quit early, don't do more checks

        logging.getLogger().info("Expected Replicas: %s", expected_replicas)
        if len(pods) != expected_replicas:
            result_code = 0
            logging.getLogger().critical("Count Pods and Replicas don't match")

        count_pods_running = len([i for i in pods if i['status'] == "Running"])
        logging.getLogger().info("Pods Running: %s", count_pods_running)
        if len(pods) != count_pods_running:
            result_code = 0
            logging.getLogger().critical("Some pods are not in running state")

        host_ips = set([x['hostIP'] for x in pods])
        logging.getLogger().info("Hosts found: %d", len(host_ips))
        if (len(host_ips) > len(pods)) or len(host_ips) == 1:
            result_code = 0
            logging.getLogger().critical(
                "%s has %d pods on %d hosts, not distributed",
                podname, len(pods), len(host_ips))

        if result_code == 0:
            logging.getLogger().critical("Please check pods are in running "
                                         "state, and on unique hosts")
            logging.getLogger().critical("oc get pods -n %s -o wide", self.args.namespace)

        # result_code 1 means the pods are on different nodes
        # count_pods_running means the running pod number
        self.send_metrics(keybase=keybase, location=result_code, status=count_pods_running)

    def send_metrics(self, keybase="", location="", status=""):
        """send_metrics"""
        ms = MetricSender(verbose=self.args.verbose)
        ms.add_metric({keybase + '.location': location})
        ms.add_metric({keybase + '.status': status})
        ms.send_metrics()

def parse_args():
    """ parse the args from the cli """
    logging.getLogger().debug("parse_args()")

    parser = argparse.ArgumentParser(description='AWS instance health')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level, specify multiple')
    parser.add_argument('--namespace', default="default",
                        help='Project namespace')
    args = parser.parse_args()

    if args.verbose > 0:
        logging.getLogger().setLevel(logging.DEBUG)

    return args

if __name__ == '__main__':
    INPS = InfraNodePodStatus(args=parse_args(), )
    INPS.check_pods('router', keybase="openshift.router.pod", )
    INPS.check_pods('docker-registry', keybase="openshift.registry.pod", )
    INPS.check_pods('router2', keybase="openshift.router2.pod", pod_optional=True, )
