#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Custom filters for operations use
"""

import pdb
from ansible import errors
from collections import Mapping
from jinja2.utils import soft_unicode

class FilterModule(object):
    """ Custom ansible filters """

    @staticmethod
    def ops_pdb(arg):
        """ This pops you into a pdb instance where arg is the data passed in
            from the filter.
            Ex: "{{ hostvars | oo_pdb }}"
        """
        pdb.set_trace()
        return arg

    @staticmethod
    def ops_flatten(data):
        """ This filter plugin will flatten a list of lists
        """
        if not isinstance(data, list):
            raise errors.AnsibleFilterError("|failed expects to flatten a List")

        return [item for sublist in data for item in sublist]

    @staticmethod
    def ops_select_keys(data, keys):
        """ This returns a list, which contains the value portions for the keys
            Ex: data = { 'a':1, 'b':2, 'c':3 }
                keys = ['a', 'c']
                returns [1, 3]
        """

        if not isinstance(data, Mapping):
            raise errors.AnsibleFilterError("|failed expects to filter on a dict or object")

        if not isinstance(keys, list):
            raise errors.AnsibleFilterError("|failed expects first param is a list")

        # Gather up the values for the list of keys passed in
        retval = [data[key] for key in keys if key in data]

        return retval

    @staticmethod
    def ops_select_keys_from_list(data, keys):
        """ This returns a list, which contains the value portions for the keys
            Ex: data = { 'a':1, 'b':2, 'c':3 }
                keys = ['a', 'c']
                returns [1, 3]
        """

        if not isinstance(data, list):
            raise errors.AnsibleFilterError("|failed expects to filter on a list")

        if not isinstance(keys, list):
            raise errors.AnsibleFilterError("|failed expects first param is a list")

        # Gather up the values for the list of keys passed in
        retval = [FilterModule.ops_select_keys(item, keys) for item in data]

        return FilterModule.ops_flatten(retval)

    @staticmethod
    def ops_get_attr(data, attribute=None):
        """ This looks up dictionary attributes of the form a.b.c and returns
            the value.
            Ex: data = {'a': {'b': {'c': 5}}}
                attribute = "a.b.c"
                returns 5
        """
        if not attribute:
            raise errors.AnsibleFilterError("|failed expects attribute to be set")

        ptr = data
        for attr in attribute.split('.'):
            ptr = ptr[attr]

        return ptr

    @staticmethod
    def ops_collect(data, attribute=None, filters=None):
        """ This takes a list of dict and collects all attributes specified into a
            list. If filter is specified then we will include all items that
            match _ALL_ of filters.  If a dict entry is missing the key in a
            filter it will be excluded from the match.
            Ex: data = [ {'a':1, 'b':5, 'z': 'z'}, # True, return
                         {'a':2, 'z': 'z'},        # True, return
                         {'a':3, 'z': 'z'},        # True, return
                         {'a':4, 'z': 'b'},        # FAILED, obj['z'] != obj['z']
                       ]
                attribute = 'a'
                filters   = {'z': 'z'}
                returns [1, 2, 3]
        """
        if not isinstance(data, list):
            raise errors.AnsibleFilterError("|failed expects to filter on a List")

        if not attribute:
            raise errors.AnsibleFilterError("|failed expects attribute to be set")

        if filters is not None:
            if not isinstance(filters, dict):
                raise errors.AnsibleFilterError("|failed expects filter to be a"
                                                " dict")
            retval = [FilterModule.ops_get_attr(d, attribute) for d in data if (
                all([d.get(key, None) == filters[key] for key in filters]))]
        else:
            retval = [FilterModule.ops_get_attr(d, attribute) for d in data]

        return retval

    @staticmethod
    def ops_get_hosts_from_hostvars(hostvars, hosts):
        """ Return a list of hosts from hostvars """
        retval = []
        for host in hosts:
            try:
                retval.append(hostvars[host])
            except errors.AnsibleError as _:
                # host does not exist
                pass

        return retval

    # adapted from https://gist.github.com/halberom/b1f6eaed16dba1b298e8

    @staticmethod
    def ops_map_format(value, pattern, *args):
        """
        Apply python string formatting on an object:
        .. sourcecode:: jinja
            {{ my_list | map("ops_map_format", "Item {0}") | list }}
                -> [ "Item 1", "Item 2", "Item 3" ]
        """
        return soft_unicode(pattern).format(value, *args)

    def filters(self):
        """ returns a mapping of filters to methods """
        return {
            "ops_pdb": self.ops_pdb,
            "ops_select_keys_from_list": self.ops_select_keys_from_list,
            "ops_flatten": self.ops_flatten,
            "ops_select_keys": self.ops_select_keys,
            "ops_get_attr": self.ops_get_attr,
            "ops_collect": self.ops_collect,
            "ops_get_hosts_from_hostvars": self.ops_get_hosts_from_hostvars,
            "ops_map_format": self.ops_map_format,
        }
