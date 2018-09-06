#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script is used to check the psad logs for positive port scanning traffic
 and report its findings to Zabbix.
"""

from __future__ import print_function
from datetime import datetime

import os
import re

import boto3
import botocore
import yaml

# Reason: disable pylint import-error because our modules aren't loaded on jenkins.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


class CheckStatus(object):
    """ Class to check for issues found in psad logs. """


    @staticmethod
    def check_psad(log_message, logfile):
        """ Check number of occurrences of issues in the specified logfile.

            Returns:
                An int representing the number of issues found.
         """

        total_issues = 0

        if os.path.isfile(logfile):
            with open(logfile) as open_file:
                stripped_line = list([line.rstrip() for line in open_file.readlines()])
                for line in stripped_line:
                    line_found = re.search(log_message, line, re.IGNORECASE)
                    if line_found:
                        total_issues += 1

                return total_issues
        else:
            raise ValueError(logfile + ' does not exist.')


    @staticmethod
    def search_logfile(logfile):
        """ Look for positive scan results. """

        results = []

        with open(logfile) as open_file:
            between = False
            for line in open_file:
                tline = line.strip()
                if tline == 'iptables auto-blocked IPs:':
                    between = True
                elif tline == 'Total protocol packet counters:':
                    between = False
                elif between and tline != '':
                    results.append(tline)

        issues = len(results)

        return issues


    @staticmethod
    def get_config(config_path):
        """ Open and read config data from the variables file. """

        config_settings = {}

        if os.path.isfile(config_path):
            with open(config_path, 'r') as scan_config:
                yaml_config = yaml.load(scan_config)

                if yaml_config['opsad_creds_file']:
                    config_settings['opsad_creds_file'] = yaml_config['opsad_creds_file']

                if yaml_config['opsad_s3_bucket']:
                    config_settings['opsad_s3_bucket'] = yaml_config['opsad_s3_bucket']

                if yaml_config['opsad_log_file']:
                    config_settings['opsad_log_file'] = yaml_config['opsad_log_file']

                if yaml_config['opsad_host_name']:
                    config_settings['opsad_host_name'] = yaml_config['opsad_host_name']

                if yaml_config['opsad_cluster_name']:
                    config_settings['opsad_cluster_name'] = yaml_config['opsad_cluster_name']

        return config_settings


    @staticmethod
    def upload_data(config_dict):
        """ Use the current AWS_PROFILE to upload files to the specified bucket.

        Raises:
            A ValueError if the specified bucket can not be found.
        """


        logfile = config_dict['opsad_log_file']
        hostname = config_dict['opsad_host_name']
        credsfile = config_dict['opsad_creds_file']
        bucket = config_dict['opsad_s3_bucket']
        cluster = config_dict['opsad_cluster_name']

        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = credsfile

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

            if os.path.isfile(logfile):
                print('\nUploading logfile to %s bucket.' % bucket)
                with open(logfile) as open_file:
                    log_data = open_file.read()

                    bucket_path = cluster + '/' + \
                                  hostname + '/' + \
                                  datetime.utcnow().strftime('%Y') + '/' + \
                                  datetime.utcnow().strftime('%m') + '/' + \
                                  datetime.utcnow().strftime('%d') + '_status.txt'

                    s3_bucket.put_object(Key=bucket_path, Body=log_data)

            else:
                raise ValueError(logfile + ' does not exist.')

        else:
            raise ValueError(bucket + ' does not exist.')


    #pylint: disable=no-member
    def main(self):
        """ Main function. """

        zag = ZaggSender()

        config_dict = self.get_config('/etc/openshift_tools/scanreport_config.yml')

        logfile = config_dict['opsad_log_file']
        result_status = self.search_logfile(logfile)

        check = 'psad.found.scanner'

        zag.add_zabbix_keys({check: result_status})
        zag.send_metrics()

        if result_status > 0:
            self.upload_data(config_dict)


if __name__ == '__main__':
    PSAD_STATUS = CheckStatus()
    PSAD_STATUS.main()
