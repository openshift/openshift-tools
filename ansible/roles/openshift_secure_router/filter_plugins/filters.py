#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for use in openshift_secure_router
'''

class FilterModule(object):
    ''' Custom ansible filters '''

    @staticmethod
    def ossr_create_port_list(port_list):
        ''' given the routers' listeners list (elb port details),
            build list of OpenShift router port mappings '''

        router_port_list = []
        for ports in port_list:
            # instance port -> instance port mapping because the router
            # uses host networking
            inst_port = ports['instance_port']
            router_port_list.append("{}:{}".format(inst_port, inst_port))

        return router_port_list

    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "ossr_create_port_list": self.ossr_create_port_list,
        }
