#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for use in openshift_aws_persistent_volumes
'''

class FilterModule(object):
    ''' Custom ansible filters '''

    @staticmethod
    def explode_size_count_array(input_array):
        '''  This is a filter to help with creating PV's.
             This filter could be deprecated with Ansiible 2.0.  Ansible may implement
              a different way to do this in the code without a need for a filter.

              This filter takes in an array of dict's with size and count.
              It will then explode this an return an array of all of the sizes and name them
              sequentially.

              This can then be used with Ansible's "with_items" call.

              Example:

              input_array: [{size: 5, count: 2}, {size: 1: count: 3}]

              output_array: [
                             {size: 5, name: '5g_1'},{size: 5, name: '5g_2'},
                             {size: 5, name: '1g_1'},{size: 5, name: '1g_2'},{size: 5, name: '1g_3'}
                            ]
        '''
        rval = []

        for array_item in input_array:
            for i in range(1, array_item["count"] + 1):
                #rval.append({"size": array_item["size"], "name": "%sg-%03d" %(array_item['size'], i)})
                rval.append({"size": array_item["size"], "name": "%sg-%d" %(array_item['size'], i)})

        return rval


    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "explode_size_count_array": self.explode_size_count_array,
        }
