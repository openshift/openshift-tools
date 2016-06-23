#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Custom filters for operations use
"""

import pdb

class FilterModule(object):
    """ Custom ansible filters """

    @staticmethod
    def oo_pdb(arg):
        """ This pops you into a pdb instance where arg is the data passed in
            from the filter.
            Ex: "{{ hostvars | oo_pdb }}"
        """
        pdb.set_trace()
        return arg

    def filters(self):
        """ returns a mapping of filters to methods """
        return {
            "oo_pdb": self.oo_pdb,
        }
