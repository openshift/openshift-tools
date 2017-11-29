#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script is used to check the clam update timestamp and report to Zabbix.
 It will report an issue to Zabbix if the stamp file is older than 2 weeks.
"""

from __future__ import print_function

import os
import time
import yaml

# Reason: disable pylint import-error because our modules aren't loaded on jenkins.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


class CheckStatus(object):
    """ Class to check the age of clam_update's timestamp file.
        Alerts to Zabbix if stamp is older than 2 weeks.
    """


    def __init__(self):
        self.time_stamp = None


    @staticmethod
    def get_config(config_path):
        """ Open and read config data from the variables file. """

        config_settings = {}

        if os.path.isfile(config_path):
            with open(config_path, 'r') as clam_config:
                yaml_config = yaml.load(clam_config)

                if yaml_config['ocav_timestamp_path']:
                    config_settings['ocav_timestamp_path'] = yaml_config['ocav_timestamp_path']

        return config_settings


    @staticmethod
    def check_clam(time_stamp):
        """ Check if the timestamp is older than 2 weeks for the provided time_stamp file. """

        total_issues = 0

        if os.path.isfile(time_stamp):
            with open(time_stamp) as open_file:
                write_date = open_file.readline().strip()
                if int(write_date) < int(time.time()) - (2 * 7 * 24 * 60 * 60):
                    total_issues += 1

                return total_issues

        else:
            total_issues += 1
            return total_issues


    def main(self):
        """ Main function. """

        zag = ZaggSender()

        config_path = '/secrets/aws_config.yml'
        config_file = self.get_config(config_path)

        time_stamp_path = config_file['ocav_timestamp_path']
        check = 'clam.update.signatures.not.updating'

        stamp_status = self.check_clam(time_stamp_path)

        zag.add_zabbix_keys({check: stamp_status})
        zag.send_metrics()


if __name__ == '__main__':
    CLAM_STATUS = CheckStatus()
    CLAM_STATUS.main()
