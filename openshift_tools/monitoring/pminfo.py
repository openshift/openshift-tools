#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4

'''
PMInfo Python implementation
'''

#
# Copyright (C) 2014 Red Hat.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#

# Our buildbot does not have the pcp libraries installed and most likely
# will never have them since this runs in a container.
# pylint: disable=import-error
from pcp import pmapi
import re

class PMInfo(object):
    """ Looks up values from pcp through the pmapi.
    """

    def __init__(self):
        """ Construct object - prepare for command line handling """
        self.context = None
        self.metrics = []

    def extract_value(self, valfmt, vlist, typ):
        '''
        Perform the extract and return an atom
        '''
        atom = self.context.pmExtractValue(valfmt, vlist, typ, typ)
        return atom.dref(typ)


    def get_value(self, metrics):
        '''Receive a list of metrics and query pcp
           libs for descriptions and values
        '''
        rval = {}
        pmids = self.context.pmLookupName(metrics)
        descs = self.context.pmLookupDescs(pmids)
        results = self.context.pmFetch(pmids)

        for i in range(results.contents.numpmid):
            num_vals = results.contents.get_numval(i)
            m_name = None
            # if num_vals is > 1 we have multiple instances returned
            # query for the names so we can generate the keys
            if num_vals > 1:
                m_name = metrics[i] + '.'
                text_descs = self.context.pmGetInDom(descs[i])
            else:
                m_name = metrics[i]
            for j in range(num_vals):
                desc = ''
                try:
                    m_value = self.extract_value(results.contents.get_valfmt(i),
                                                 results.contents.get_vlist(i, j),
                                                 descs[i].contents.type)
                except pmapi.pmErr:
                    #Impossible value or scale conversion
                    rval[m_name] = m_value
                    continue

                if num_vals > 1:
                    desc = re.sub(' ', '_', text_descs[1][j])

                rval[m_name + desc] = m_value
        return rval

    def get_children(self, root_string=''):
        ''' Return all metrics
        '''
        status = self.context.pmGetChildrenStatus(root_string)

        # Status on leaf nodes is (None,None)
        if not status[0]:
            self.metrics.append(root_string)
            return

        zipped_status = zip(status[0], status[1])
        for child in zipped_status:
            if root_string != '':
                child_name = root_string + "." + child[0]
            else:
                child_name = child[0]

            if child[1] == 0:
                self.metrics.append(child_name)
            else:
                self.get_children(child_name)

    def execute(self, metrics=None):
        """ Using a PMAPI context (could be either host or archive),
            fetch and show all of the values
        """
        if not metrics:
            self.get_children()
        else:
            for metric in metrics:
                self.get_children(metric)
        return self.get_value(self.metrics)

    def connect(self):
        """ Establish a PMAPI context to archive, host or local, via args """
        self.context = pmapi.pmContext()

def get_metrics(metrics=None):
    '''Get a list of metrics and query pcp for their values
    '''
    try:
        pcp = PMInfo()
        pcp.connect()
        return pcp.execute(metrics)
    except pmapi.pmErr as error:
        print error.message()
    except pmapi.pmUsageErr as usage:
        usage.message()
    except KeyboardInterrupt:
        pass
