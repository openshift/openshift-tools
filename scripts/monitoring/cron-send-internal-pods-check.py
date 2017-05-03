#!/usr/bin/env python

'''
  Send Cluster Infra node's pod status to Zagg
'''
#pylint: disable=import-error
#pylint: disable=invalid-name

from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

class InfraNodePodStatus(object):
    '''
      This is a check for making sure the internal pods like
      router and registry running and located on different infra nodes
    '''
    def __init__(self):
        '''initial for the InfraNodePodStatus'''
        self.kubeconfig = '/tmp/admin.kubeconfig'
        self.oc = OCUtil(namespace='default', config_file=self.kubeconfig)
        self.pod_report = self.check_pods()

    def check_pods(self):
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

    def compare_ip(self, keyword):
        ''' to compare the pod host ip and check the pod status '''
        pod_hostip_status = [self.pod_report[i] for i in self.pod_report.keys() if keyword in i]

        pod_run_num = 0
        for i in pod_hostip_status:
            if i['status'] == "Running":
                pod_run_num += 1
        if len(pod_hostip_status) == self.get_expected_replicas(keyword):
            if pod_hostip_status[0]['hostIP'] != pod_hostip_status[1]['hostIP']:
                # print "ok, you do not need do anything for {} pod".format(keyword)
                result_code = 1
            else:
                # print "there are something wrong, please check the pod"
                result_code = 0
        else:
            print "please check the pod"
            result_code = 0
        # result_code 1 means the two pods are on different nodes
        # pod_run_num means the running pod number
        return result_code, pod_run_num

    def run(self):
        ''' run the command and send the code to zabbix '''
        ms = MetricSender()

        # the check_value is the value to send to zabbix
        router_check_value = self.compare_ip('router')
        registry_check_value = self.compare_ip('docker-registry')
        print router_check_value, registry_check_value

        ms.add_metric({'openshift.router.pod.location': router_check_value[0]})
        ms.add_metric({'openshift.router.pod.status': router_check_value[1]})
        ms.add_metric({'openshift.registry.pod.location': registry_check_value[0]})
        ms.add_metric({'openshift.registry.pod.status': registry_check_value[1]})
        ms.send_metrics()

if __name__ == '__main__':
    INPS = InfraNodePodStatus()
    INPS.run()
