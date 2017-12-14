#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script is used to sync clam config files from an S3 bucket to a
 local directory. Both the files to be synced and the destination bucket
 are specified as variables in /etc/openshift_tools/clam_update_config.yaml.
"""

from __future__ import print_function

import os
import time
import yaml

# pylint: disable=import-error
import botocore
import boto3


class PullBucket(object):
    """ Class to download clam config files and databases from an S3 bucket. """


    @staticmethod
    def get_config(config_path):
        """ Open and read config data from the variables file. """

        config_settings = {}

        if os.path.isfile(config_path):
            with open(config_path, 'r') as clam_config:
                yaml_config = yaml.load(clam_config)

                if yaml_config['aws_creds_file']:
                    config_settings['aws_creds_file'] = yaml_config['aws_creds_file']

                if yaml_config['clam_mirror_bucket']:
                    config_settings['clam_mirror_bucket'] = yaml_config['clam_mirror_bucket']

                if yaml_config['clam_config_files']:
                    config_settings['clam_config_files'] = yaml_config['clam_config_files']

                if yaml_config['clam_timestamp_path']:
                    config_settings['clam_timestamp_path'] = yaml_config['clam_timestamp_path']

        return config_settings


    @staticmethod
    def download_files(bucket, file_list, aws_creds_file, timestamp):
        """ Use the provided credentials to download files from the specified bucket.

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
        # timestamps, then download if the bucket's files are newer

        if exists:
            s3_client = boto3.resource('s3')
            s3_bucket = s3_client.Bucket(bucket)
            time_dict = {}

            for obj in s3_bucket.objects.all():
                if obj.key in file_list:
                    time_dict[obj.key] = int(obj.last_modified.strftime('%s'))

            for clam_file in file_list:
                full_path = (os.path.join('/var/lib/clamav/', clam_file))
                if not os.path.isfile(full_path) or \
                int(os.path.getmtime(full_path)) < time_dict[clam_file]:
                    s3_bucket.meta.client.download_file(bucket, clam_file, full_path)
                    with open(timestamp, 'w') as open_file:
                        open_file.write(str(int(time.time())))

        else:
            raise ValueError(bucket + ' does not exist.')


    def main(self):
        """ Main function. """

        config_path = '/etc/openshift_tools/clam_update_config.yaml'

        config_file = self.get_config(config_path)

        clam_bucket = config_file['clam_mirror_bucket']
        file_list = config_file['clam_config_files']
        aws_creds_file = config_file['aws_creds_file']
        timestamp = config_file['clam_timestamp_path']

        self.download_files(clam_bucket, file_list, aws_creds_file, timestamp)


if __name__ == '__main__':
    BUCKET = PullBucket()
    BUCKET.main()
