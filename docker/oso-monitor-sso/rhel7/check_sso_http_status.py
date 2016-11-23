#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script is used to check the return code from /status.php IDP host and report to Zabbix.
 It will report an issue to Zabbix if any received HTTP status codes != 200.
"""

from __future__ import print_function

class CheckStatus(object):
    """ Class to check HTTP status code from IDP host. """

    def __init__(self):
        self.status_code = None


    @staticmethod
    def check_http():
        pass


    def main(self):
        pass

if __name__ == '__main__':
    HTTP_STATUS = CheckStatus()
    HTTP_STATUS.main()
