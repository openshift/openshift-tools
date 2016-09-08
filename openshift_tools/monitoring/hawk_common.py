# vim: expandtab:tabstop=4:shiftwidth=4
"""
hawk_common contains common data structures and utils

Example usage:
    from openshift_tools.monitoring.hawk_common import HawkConnection, HawkHeartbeat

    ZAGGCONN = HawkConnection(url='172.17.0.151', user='admin', password='pass')
    ZAGGHEARTBEAT = HawkHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

"""
from collections import namedtuple
from urlparse import urlparse
import ssl

# pylint: disable=too-few-public-methods
# This is a DTO.  It needs to be a class because we need default values
class HawkConnection(object):
    ''' DTO for hawkular connection
    '''
    # pylint: disable=too-many-arguments
    # This now supports ssl and need a couple of extra params
    def __init__(self, url, user, password, ssl_verify=False, debug=False, inactive=False):
        self.url = url if url.startswith('http') else 'http://' + url
        self.username = user
        self.password = password
        self.ssl_verify = ssl_verify
        self.debug = debug
        self.inactive = inactive # We do not want this lib to work ansless explisitly activated

        url_params = urlparse(self.url)
        self.host = url_params.hostname
        self.scheme = url_params.scheme
        self.port = url_params.port or {'http': 80, 'https': 443}[self.scheme]
        self.context = context=None if self.ssl_verify else ssl._create_unverified_context()
        self.tenant_id = '_ops'

HawkHeartbeat = namedtuple("HawkHeartbeat", ["templates", "hostgroups"])
