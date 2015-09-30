# vim: expandtab:tabstop=4:shiftwidth=4
"""
zagg_common contains common data structures and utils

Example usage:
    from openshift_tools.monitoring.zagg_common import ZaggConnection, ZaggHeartbeat

    ZAGGCONN = ZaggConnection(host='172.17.0.151', user='admin', password='pass')
    ZAGGHEARTBEAT = ZaggHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

"""
from collections import namedtuple

# pylint: disable=too-few-public-methods
# This is a DTO.  It needs to be a class because we need default values
class ZaggConnection(object):
    ''' DTO for zabbix connection
    '''
    # pylint: disable=too-many-arguments
    # This now supports ssl and need a couple of extra params
    def __init__(self, url, user, password, ssl_verify=False, verbose=False):
        self.url = url
        self.user = user
        self.password = password
        self.ssl_verify = ssl_verify
        self.verbose = verbose


ZaggHeartbeat = namedtuple("ZaggHeartbeat", ["templates", "hostgroups"])
