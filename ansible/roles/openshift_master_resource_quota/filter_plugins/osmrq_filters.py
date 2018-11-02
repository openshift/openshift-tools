#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
"""
Custom filters for use in openshift-ansible
"""

from ansible import errors


def osmrq_get_existing_namespaces(oc_obj_namespaces_list):
    '''Take the output of the oc_obj namespaces list and return a list of namespaces that are foun

    - oc_obj
    '''
    valid_namespace_list = []
    for namespace in oc_obj_namespaces_list:
        if 'kind' in namespace['results']['results'][0]:

            valid_namespace_list.append(namespace['item'])

    return valid_namespace_list


class FilterModule(object):
    """ Custom ansible filter mapping """

    # pylint: disable=no-self-use, too-few-public-methods
    def filters(self):
        """ returns a mapping of filters to methods """
        return {
            "osmrq_get_existing_namespaces": osmrq_get_existing_namespaces,
        }
