#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Generic REST class using python requests module

see zagg_client.py for example on how to use

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
    def __init__(self, host=None, username=None, password=None, headers=None, token=None):

        self.hosts = host
        self.username = username
        self.password = password
        self.token = token
        self.headers = headers

        self.base_uri = "http://" + host + "/"

    @property
    def _auth(self):
        """
        implement authentication for the rest call
        """
        if self.username and self.password:
            return requests.auth.HTTPBasicAuth(self.username, self.password)
        return None

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
            auth=None if not self._auth else self._auth,
            method=method, url=url, params=params, data=data,
            headers=_headers, timeout=130, verify=False
        )

        data = None
        if response.status_code == 200:
            data = response.json()

        return (response.status_code, data)
