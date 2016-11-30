#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for use in openshift_aws_pv_move
'''

class FilterModule(object):
    ''' Custom ansible filters '''

    @staticmethod
    def osapm_pvs_in_az(pvs, from_az):
        ''' given a list of PVs, return a list of PVs in AZ from_az '''

        new_pvs = []
        for pvol in pvs:
            if from_az in pvol['metadata']['labels']['failure-domain.beta.kubernetes.io/zone']:
                volumeid = pvol['spec']['awsElasticBlockStore']['volumeID']
                # possible formats: aws://az/volume_id or just a volumeid
                volumeid = volumeid.split('/')[-1]
                new_pvs.append({'pv_name': pvol['metadata']['name'],
                                'volumeid': volumeid})

        return new_pvs

    @staticmethod
    def osapm_movable_pvs(pvs, snapshots):
        ''' given a list of pvs and all snapshots in region
            return list of PVs that have snapshots available '''

        movable_pvs = []

        for pvol in pvs:
            for snap in snapshots:
                if pvol['volumeid'] == snap['volume_id']:
                    movable_pvs.append(pvol)
                    break

        return movable_pvs

    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "osapm_pvs_in_az": self.osapm_pvs_in_az,
            "osapm_movable_pvs": self.osapm_movable_pvs,
        }
