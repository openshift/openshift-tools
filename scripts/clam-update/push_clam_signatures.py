#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script is used to sync clam config files from a container
 to an S3 bucket. Both the files to be synced and the destination
 bucket are specified as variables in /secrets/aws_config.yml
 """

from __future__ import print_function

import os
import time
import yaml

# pylint: disable=import-error
import botocore
import boto3


class UpdateBucket(object):
    """ Class to upload clam config files and databases to an S3 bucket. """


    @staticmethod
    def get_config(config_path):
        """ Open and read config data from the variables file. """

        config_settings = {}

        if os.path.isfile(config_path):
            with open(config_path, 'r') as clam_config:
                yaml_config = yaml.load(clam_config)

                if yaml_config['ocav_ops_files']:
                    config_settings['ocav_ops_files'] = yaml_config['ocav_ops_files']

                if yaml_config['ocav_s3_bucket']:
                    config_settings['ocav_s3_bucket'] = yaml_config['ocav_s3_bucket']

                if yaml_config['ocav_creds_file']:
                    config_settings['ocav_creds_file'] = yaml_config['ocav_creds_file']

                if yaml_config['ocav_timestamp_path']:
                    config_settings['ocav_timestamp_path'] = yaml_config['ocav_timestamp_path']

        return config_settings


    @staticmethod
    # pylint: disable=too-many-locals
    def upload_files(bucket, file_list, aws_creds_file, timestamp):
        """ Use the provided credentials to upload files to the specified bucket.

        Raises:
            A ValueError if the specified bucket can not be found.
        """

        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = aws_creds_file

        s3_session = boto3.resource('s3')
        exists = True

        try:
            s3_session.meta.client.head_bucket(Bucket=bucket)

        except botocore.exceptions.ClientError as client_exception:
            error_code = int(client_exception.response['Error']['Code'])

            if error_code == 404:
                exists = False

        # get timestamps of all items in bucket, compare with local
        # timestamps, then upload if the local files are newer

        if exists:
            s3_client = boto3.resource('s3')
            s3_bucket = s3_client.Bucket(bucket)

            time_dict = {}
            for obj in s3_bucket.objects.all():
                if obj.key in file_list:
                    time_dict[obj.key] = int(obj.last_modified.strftime('%s'))

            for clam_file in file_list:
                full_path = (os.path.join('/var/lib/clamav/', clam_file))
                if os.path.isfile(full_path) and \
                int(os.path.getmtime(full_path)) > time_dict[clam_file]:
                    sig_data = open(full_path, 'rb')
                    s3_bucket.put_object(Key=clam_file, Body=sig_data)
                    with open(timestamp, 'w') as open_file:
                        open_file.write(str(int(time.time())))

        else:
            raise ValueError(bucket + ' does not exist.')


    def main(self):
        """ Main function. """

        config_path = '/secrets/aws_config.yml'

        config_file = self.get_config(config_path)

        clam_bucket = config_file['ocav_s3_bucket']
        config_list = config_file['ocav_ops_files']
        aws_creds_file = config_file['ocav_creds_file']
        timestamp = config_file['ocav_timestamp_path']

        self.upload_files(clam_bucket, config_list, aws_creds_file, timestamp)


if __name__ == '__main__':
    BUCKET = UpdateBucket()
    BUCKET.main()
