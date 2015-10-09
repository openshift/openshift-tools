#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Generic REST class using python requests module

see zagg_client.py for example on how to use

"""
import requests
# pylint: disable=import-error,no-name-in-module
import requests.packages.urllib3.connectionpool as httplib
import urllib3

from urllib3.contrib import pyopenssl
pyopenssl.inject_into_urllib3()

#Currently only one method is used.
#More will be added in the future, and this can be disabled
#pylint: disable=too-few-public-methods
class RestApi(object):
    """
    A base connection class to derive from.
    """

    # All args are required
    #pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(self,
                 host=None,
                 username=None,
                 password=None,
                 headers=None,
                 token=None,
                 ssl_verify=False,
                 debug=False):

        self.host = host
        self.username = username
        self.password = password
        self.token = token
        self.headers = headers
        self.ssl_verify = ssl_verify
        self.debug = debug

        if self.debug:
            httplib.HTTPConnection.debuglevel = 1
            httplib.HTTPSConnection.debuglevel = 1

        self.base_uri = "http://" + self.host + "/"

    @property
    def _auth(self):
        """
        implement authentication for the rest call
        """
        if self.username and self.password:
            return requests.auth.HTTPBasicAuth(self.username, self.password)
        return None

    def request(self, url, method, timeout=120, headers=None, params=None, data=None):
        """
        wrapper method for Requests' methods
        """
        if not url.startswith("https://") and not url.startswith("http://"):
            url = self.base_uri + url

        # This will disable the SSL warning for certificate verification
        if not self.ssl_verify and url.startswith('https://'):
            urllib3.disable_warnings()

            # pylint: disable=no-member
            requests.packages.urllib3.disable_warnings()

        _headers = self.headers or {}

        if headers:
            _headers.update(headers)

        response = requests.request(
            auth=None if not self._auth else self._auth,
            allow_redirects=True,
            method=method,
            url=url,
            params=params,
            data=data,
            headers=_headers,
            timeout=timeout,
            verify=self.ssl_verify,
        )

        data = None
        if response.status_code == 200:
            data = response.json()

        return (response.status_code, data)
