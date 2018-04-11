#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

""" Class to take image-inspector scan results and upload them to an S3 bucket. """

from datetime import datetime

import os
import yaml

# pylint: disable=import-error
import botocore
import boto3


class ClamLogUpload(object):
    """ Class to upload scan results to an S3 bucket. """


    @staticmethod
    def get_config(config_path):
        """ Open and read config data from the variables file. """

        config_settings = {}

        if os.path.isfile(config_path):
            with open(config_path, 'r') as log_config:
                yaml_config = yaml.load(log_config)

                try:
                    config_settings['oii_s3_bucket'] = yaml_config['oii_s3_bucket']
                except KeyError:
                    pass

                try:
                    config_settings['oii_creds_file'] = yaml_config['oii_creds_file']
                except KeyError:
                    pass

                try:
                    config_settings['oii_ops_files'] = yaml_config['oii_ops_files']
                except KeyError:
                    pass

                try:
                    config_settings['node_hostname'] = yaml_config['node_hostname']
                except KeyError:
                    pass

                try:
                    config_settings['cluster_name'] = yaml_config['cluster_name']
                except KeyError:
                    pass

        return config_settings


    # pylint: disable=too-many-locals
    def upload_files(self):
        """ Use the provided credentials to upload files to the specified bucket.

        Raises:
            A ValueError if the specified bucket can not be found.
        """

        config_file = self.get_config('/secrets/aws_config.yml')
        hostname_file = self.get_config('/etc/openshift_tools/scanreport_config.yml')

        bucket = config_file['oii_s3_bucket']
        file_list = config_file['oii_ops_files']
        aws_creds_file = config_file['oii_creds_file']
        node_hostname = hostname_file['node_hostname']
        cluster_name = hostname_file['cluster_name']

        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = aws_creds_file

        s3_session = boto3.resource('s3')
        exists = True

        try:
            s3_session.meta.client.head_bucket(Bucket=bucket)

        except botocore.exceptions.ClientError as client_exception:
            error_code = int(client_exception.response['Error']['Code'])

            if error_code == 404:
                exists = False

        if exists:
            s3_client = boto3.resource('s3')
            s3_bucket = s3_client.Bucket(bucket)

            cur_time = datetime.now().strftime('%Y%m%d')

            for report_file in file_list:
                full_path = (os.path.join('/var/log/clam/', report_file))
                if os.path.isfile(full_path):
                    report_data = open(full_path, 'rb')
                    upload_path = cluster_name + '/' + cur_time +\
                                  '/' + node_hostname + '/' + report_file
                    s3_bucket.put_object(Key=upload_path, Body=report_data)

                    # pylint: disable=no-member
                    os.replace(full_path, full_path + '.last')

        else:
            raise ValueError(bucket + ' does not exist.')


    def main(self):
        """ Main function. """

        self.upload_files()


if __name__ == '__main__':
    FILEUPLOAD = ClamLogUpload()
    FILEUPLOAD.main()
