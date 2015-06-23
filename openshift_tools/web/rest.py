#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Generic REST class using python requests module

"""

import requests

#Currently only one method is used.
#More will be added in the future, and this can be disabled
#pylint: disable=too-few-public-methods
class RestApi(object):
    """
    A base connection class to derive from.
    """

    # All args are required
    #pylint: disable=too-many-arguments
    def __init__(self, host=None, username=None, password=None, headers=None):

        if host is not None:
            self.host = host

        if username:
            self.username = username

        if password:
            self.password = password

        if headers:
            self.headers = headers

        self.base_uri = "http://" + host + "/"
        self.data = None

    def request(self, url, method, headers=None, params=None, data=None):
        """
        wrapper method for Requests' methods
        """
        if not url.startswith("https://") or not url.startswith("http://"):
            url = self.base_uri + url
        _headers = self.headers or {}
        if headers:
            _headers.update(headers)

        response = requests.request(
            auth=None, method=method, url=url, params=params, data=data,
            headers=_headers, timeout=130, verify=False
        )

        self.data = response.json()

        return (response.status_code, self.data)
