#!/usr/bin/python

# Copyright 2015 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author:  Andy Grimm <agrimm@redhat.com>
# Purpose: Demonstrate how to obtain Red Hat SSO credentials from a script
#

import BeautifulSoup
import requests
from requests.packages.urllib3.connectionpool import InsecureRequestWarning
import requests.auth
from requests.cookies import extract_cookies_to_jar
import json
import re
import os
import warnings
import yaml
from cookielib import LWPCookieJar

class SAMLAuth(requests.auth.AuthBase):
    def __init__(self, session):
        # This points back to the parent session
        self.session = session

    def handle_auth(self, r, **kwargs):
        """Takes the given response and tries SAML auth, if needed."""

        if r.status_code not in [ 401, 403 ]:
          return r

        # Consume content and release the original connection
        # to allow our new request to reuse the same one.
        r.content
        r.raw.release_conn()
        prep = r.request.copy()
        extract_cookies_to_jar(prep._cookies, r.request, r.raw)
        cookie_dict = requests.utils.dict_from_cookiejar(prep._cookies)

        self.session.auth = None
        self.session.get_sso_cookie()
        self.session.auth = self

        prep.prepare_cookies(self.session.cookies)

        _r = r.connection.send(prep, **kwargs)
        _r.history.append(r)
        _r.request = prep

        return _r

    def __call__(self, r):
        r.register_hook('response', self.handle_auth)
        return r

class SAMLAuthSession(requests.sessions.Session):
    def __init__(self, *args, **kwargs):
        for kw in [ 'idp_url', 'sp_url', 'auth_params',
                    'sso_cookie_name', 'cookie_jar_path' ]:
            setattr(self, kw, kwargs.get(kw, None))
            # TODO: Error checking
        super(SAMLAuthSession, self).__init__()
        self.auth = SAMLAuth(self)
        if self.cookie_jar_path is not None:
            self.initialize_cookie_jar()
        warnings.simplefilter("ignore", InsecureRequestWarning)

    def initialize_cookie_jar(self):
        self.cookies = LWPCookieJar(self.cookie_jar_path)
        if not os.path.exists('cookiejar'):
            # Create a new cookies file and set our Session's cookies
            self.cookies.save()
        self.cookies.load(ignore_discard=True)

    def get_sso_cookie(self):
        cookie_dict = requests.utils.dict_from_cookiejar(self.cookies)
        # TODO: check for expired cookies, since we are doing ignore_discard=True
        if self.sso_cookie_name not in cookie_dict.keys():
            # This request gets us some initial cookies like JSESSION
            # I have no idea what the generalized form of this should be.
            # Maybe instead of initializing with username/password, I should actually
            # be taking a params dict.
            resp = self.get(self.idp_url, params=self.auth_params)

            # Request protected resource from Service Provider (SP)
            resp2 = self.get(self.sp_url)
            # Post SAML AuthN to Identity Provider (IdP)
            resp3 = self.parse_and_post_form(resp2.text)
            # Post SAML Assertion to SP
            resp4 = self.parse_and_post_form(resp3.text)
            # ... and one more redirect?
            resp5 = self.parse_and_post_form(resp4.text)
            # TODO: Check all the http statuses and error if we don't get the
            # SSO cookie here.
            self.cookies.save(ignore_discard=True)

    def parse_and_post_form(self, htmldata):
        dom = BeautifulSoup.BeautifulSoup(htmldata)
        form = dom.find("form")
        params = {}
        for input_field in form.findAll("input", { 'type': re.compile('hidden', re.IGNORECASE) }):
            params[input_field['name']] = input_field['value']

        return self.post(form['action'], data=params)

'''
Example YAML config:

idp_url: 'https://idp.redhat.com/idp/authUser'
sp_url:  'https://gss.my.salesforce.com'
test_url: 'https://unified.gsslab.rdu2.redhat.com/user?where=%28sbrName%20is%20%22Shift%22%20or%20roleSbrName%20is%20%22Shift%22%29'
auth_params:
  j_username: 'rhn-support-XXXXXXX'
  j_password: 's3kr1t'
  redirect:   'https://gss.my.salesforce.com'
sso_cookie_name: 'rh_sso'
cookie_jar_path: 'cookiejar'
'''

if __name__ == "__main__":
    cfg = yaml.load(open('saml_auth.yaml').read())
    s = SAMLAuthSession(**cfg)
    resp = s.get(cfg['test_url'], verify=False)
    print resp.text
    s.cookies.save(ignore_discard=True)
