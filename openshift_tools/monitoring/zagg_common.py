# vim: expandtab:tabstop=4:shiftwidth=4
"""
zagg_common contains common data structures and utils

Example usage:
    from openshift_tools.monitoring.zagg_common import ZaggConnection, ZaggHeartbeat

    ZAGGCONN = ZaggConnection(host='172.17.0.151', user='admin', password='pass')
    ZAGGHEARTBEAT = ZaggHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

"""
from collections import namedtuple

ZaggConnection = namedtuple("ZaggConnection", ["host", "user", "password"])

ZaggHeartbeat = namedtuple("ZaggHeartbeat", ["templates", "hostgroups"])
