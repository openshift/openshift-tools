#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for use in openshift_sso_app
'''

class FilterModule(object):
    ''' Custom ansible filters '''

    @staticmethod
    def get_running_pods(podlist_results, pod_names_to_match):
        '''  This is a filter to see which pods in a project are running

              This filter takes the

              Example:

              given this:

              podlist_results:
                results:
                  - items:
                      - status:
                          phase: Running
                        metadata:
                          labels:
                            deploymentconfig: oso-memcached-sso1
                      - status:
                          phase: Terminated
                        metadata:
                          labels:
                            deploymentconfig: oso-memcached-sso2
                      - status:
                          phase: Running
                        metadata:
                          labels:
                            deploymentconfig: oso-saml-sso
                      - status:
                          phase: Running
                        metadata:
                          labels:
                            deploymentconfig: oso-saml-sso
              Then

              {{ podlist_results | get_running_pods(['oso-memcached-sso1', 'oso-memcached-sso2', ''oso-saml-sso]) }}

              gives an output of ['oso-memcached-sso1', 'oso-saml-sso', 'oso-saml-sso']
        '''
        rval = []
        if 'results' not in podlist_results:
            return rval
        if len(podlist_results['results']) == 0:
            return rval
        if 'items' not in podlist_results['results'][0]:
            return rval
        for pod in podlist_results['results'][0]['items']:
            if 'status' not in pod:
                continue
            if 'phase' not in pod['status']:
                continue
            if pod['status']['phase'] != 'Running':
                continue
            if 'metadata' not in pod or 'labels' not in pod['metadata']:
                continue
            if 'deploymentconfig' not in pod['metadata']['labels']:
                continue
            if pod['metadata']['labels']['deploymentconfig'] in pod_names_to_match:
                rval.append(pod['metadata']['labels']['deploymentconfig'])
        return rval


    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "get_running_pods": self.get_running_pods,
        }
