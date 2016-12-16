#!/usr/bin/env python
'''
ansible module for creating AWS ELB in a new AZ (from the most recent snapshot)
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   AWS ELB AZ migrator
#
#
#   Copyright 2016 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Jenkins environment doesn't have all the required libraries
# pylint: disable=import-error
import boto3

class AwsElbMigrator(object):
    '''
    ansible module for creating an ELB in the 'target_az' AZ from the most
    recent snapshot of the 'from_vol' VolumeID
    '''

    def __init__(self):
        ''' constructor '''
        self.module = None
        self.ec2_client = None

    def get_latest_snapshot(self):
        ''' return most recent snapshot for source ELB volume '''

        # Get all snapshots for the volume
        aws_filter = [{'Name': 'volume-id',
                       'Values': [self.module.params['from_vol']]},
                      {'Name': 'status',
                       'Values': ['completed']},
                     ]
        snaps = self.ec2_client.describe_snapshots(Filters=aws_filter)

        # Fail if source volume has no snapshots
        if snaps['Snapshots'] == []:
            self.module.fail_json(changed=False,
                                  msg="No snapshot found for volume " + \
                                      self.module.params['from_vol'])

        # Find most recent snapshot of the volume
        latest = None
        for snap in snaps['Snapshots']:
            if latest == None:
                latest = snap
            elif snap['StartTime'] > latest['StartTime']:
                latest = snap

        return latest['SnapshotId']

    def volume_from_snap_already_in_az(self, snapshot):
        ''' if a volume from the provided snapshot already exists
            in the target AZ, then return the volumeID,
            otherwise, return None '''

        # See if there already is an EBS volume from the provided snapshot
        # in the target_az
        vol_filter = [{'Name': 'snapshot-id',
                       'Values': [snapshot]},
                      {'Name': 'availability-zone',
                       'Values': [self.module.params['target_az']]},
                      {'Name': 'status',
                       'Values': ['creating', 'available', 'in-use']},
                     ]
        vols = self.ec2_client.describe_volumes(Filters=vol_filter)

        if vols['Volumes'] == []:
            return None

        # Return the most recent EBS volume
        latest = None
        for vol in vols['Volumes']:
            if latest == None:
                latest = vol
            elif vol['CreateTime'] > latest['CreateTime']:
                latest = vol
        return latest

    @staticmethod
    def get_volume_name(volume):
        ''' return the 'Name' tag from a volume '''

        name = None
        if volume.has_key('Tags'):
            for tag in volume['Tags']:
                if tag['Key'] == 'Name':
                    name = tag['Value']

        return name

    def create_ebs_volume(self, snapshot):
        ''' create EBS volume in target AZ from provided snapshot '''

        volume_type = None
        iops = None
        name = self.module.params['name']

        if self.module.params['volume_type']:
            volume_type = self.module.params['volume_type']
            iops = self.module.params['iops']
        else:
            # Get previous EBS details
            vol = self.ec2_client.describe_volumes(VolumeIds=[self.module.params['from_vol']])
            volume_type = vol['Volumes'][0]['VolumeType']
            iops = vol['Volumes'][0]['Iops']
            name = self.get_volume_name(vol['Volumes'][0])

        params = {'AvailabilityZone': self.module.params['target_az'],
                  'VolumeType': volume_type,
                  'SnapshotId': snapshot}

        if 'io' in volume_type:
            # provisioned iops storage 'io1' type needs the requested IOPS
            params['Iops'] = iops

        vol = self.ec2_client.create_volume(**params)

        # Tag the volume
        if name != None:
            self.ec2_client.create_tags(Resources=[vol['VolumeId']],
                                        Tags=[{'Key': 'Name', 'Value': name}])

        return vol

    def main(self):
        ''' entry point for module '''

        self.module = AnsibleModule(
            argument_spec=dict(
                region=dict(default=None, required=True, type='str'),
                target_az=dict(default=None, required=True, type='str'),
                from_vol=dict(default=None, required=True, type='str'),
                name=dict(default=None, type='str'),
                volume_type=dict(default=None, type='str',
                                 choices=['standard', 'io1', 'gp2',
                                          'sc1', 'st1']),
                iops=dict(default=None, type='int'),
                aws_access_key=dict(default=None, type='str'),
                aws_secret_key=dict(default=None, type='str'),
            ),
            #supports_check_mode=True
        )

        aws_access_key = self.module.params['aws_access_key']
        aws_secret_key = self.module.params['aws_secret_key']
        if aws_access_key and aws_secret_key:
            boto3.setup_default_session(aws_access_key_id=aws_access_key,
                                        aws_secret_access_key=aws_secret_key,
                                        region_name=self.module.params['region'])
        else:
            boto3.setup_default_session(region_name=self.module.params['region'])

        self.ec2_client = boto3.client('ec2')

        snapshot = self.get_latest_snapshot()

        volume = self.volume_from_snap_already_in_az(snapshot)
        if volume:
            results = {'source_vol': self.module.params['from_vol'],
                       'new_vol': volume}
            self.module.exit_json(changed=False,
                                  results=results)

        # else Create volume in new AZ
        volume = self.create_ebs_volume(snapshot)

        results = {'source_vol': self.module.params['from_vol'],
                   'new_vol': volume}
        self.module.exit_json(changed=True, results=results)


#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
if __name__ == '__main__':
    # Ansible modules need this wildcard import
    # pylint: disable=unused-wildcard-import, wildcard-import, redefined-builtin
    from ansible.module_utils.basic import *

    elb_migrator = AwsElbMigrator()
    elb_migrator.main()
