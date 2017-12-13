#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for use in openshift-ansible
'''

import pdb
from string import digits
import json

class FilterModule(object):
    ''' Custom ansible filters '''

    @staticmethod
    def oo_pdb(arg):
        ''' This pops you into a pdb instance where arg is the data passed in
            from the filter.
            Ex: "{{ hostvars | oo_pdb }}"
        '''
        pdb.set_trace()
        return arg

    @staticmethod
    def vol_attrs(target_volume):
        '''
            Return a json of permutations for volume name we'll need
        '''
        vol = {
            "partition": target_volume.replace("/dev/", ""),
            "device": target_volume.strip(digits),
            "bare_device": target_volume.strip(digits).replace("/dev/", ""),
            "fullname": target_volume
        }
        return json.dumps(vol)

    @staticmethod
    def get_volume_size_by_linux_device(volumes, target_volume):
        '''
            This filter matches a device string /dev/sdX to /dev/xvdX
            It will then return the AWS volume size
        '''
        for vol in volumes:
            translated_name = vol["attachment_set"]["device"].replace("sd", "xvd")
            if translated_name.startswith(target_volume):
                return vol["size"]

        return None

    @staticmethod
    def get_volume_id_by_linux_device(volumes, target_volume):
        '''
            This filter matches a device string /dev/sdX to /dev/xvdX
            It will then return the AWS volume ID
        '''
        for vol in volumes:
            translated_name = vol["attachment_set"]["device"].replace("sd", "xvd")
            if translated_name.startswith(target_volume):
                return vol["id"]

        return None

    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "get_volume_size_by_linux_device": self.get_volume_size_by_linux_device,
            "get_volume_id_by_linux_device": self.get_volume_id_by_linux_device,
            "vol_attrs": self.vol_attrs,
        }
