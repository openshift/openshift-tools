#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script is used to check the rkhunter logs for infections and report to Zabbix.
 It will report an issue to Zabbix if any lines match 'infected' or 'Warning'.
"""

# Reason: disable pylint import-error because our modules aren't loaded on jenkins.
# Reason: disable pylint invalid-name because it does not like the naming
# of the script to be different than the class name
# pylint: disable=invalid-name,import-error

from __future__ import print_function

import os
import re
import yaml

from openshift_tools.monitoring.zagg_sender import ZaggSender


class CheckStatus(object):
    """ Class to check for issues found in rkhunter logs. """


    def __init__(self):
        self.yaml_config = None


    @staticmethod
    def check_rkhunter(log_message, logfile):
        """ Check number of occurrences of the provided string in the specified logfile. """

        total_issues = 0

        if os.path.isfile(logfile):
            with open(logfile) as open_file:
                for line in open_file.readlines():
                    line_found = re.search(log_message, line.rstrip(), re.IGNORECASE)
                    if line_found:
                        total_issues += 1

                return total_issues
        else:
            raise ValueError(logfile + ' does not exist.')


    def main(self):
        """ Main function. """

        zag = ZaggSender()
        yaml_config = {}
        config_path = '/etc/openshift_tools/rkhunter_config.yaml'

        if os.path.isfile(config_path):
            with open(config_path, 'r') as rkhunter_config:
                yaml_config = yaml.load(rkhunter_config)

        logfile = yaml_config["logfile"]

        checks = {
            "rkhunter.found.warning": r"\[ warning \]",
            "rkhunter.found.infection": r"INFECTED$"
        }

        for zabbix_key, search_term in checks.iteritems():
            scan_status = self.check_rkhunter(search_term, logfile)

            zag.add_zabbix_keys({zabbix_key: scan_status})
            zag.send_metrics()


if __name__ == '__main__':
    RKHUNTER_STATUS = CheckStatus()
    RKHUNTER_STATUS.main()
