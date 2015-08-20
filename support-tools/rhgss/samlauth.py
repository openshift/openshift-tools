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

'''
Purpose: Demonstrate how to obtain Red Hat SSO credentials from a script

Example YAML config:

idp_url: 'https://idp.redhat.com/idp/authUser'
sp_url:  'https://gss.my.salesforce.com'
test_url: 'https://unified.gsslab.rdu2/user?where=(sbrName is "Shift")'
auth_params:
  j_username: 'rhn-support-XXXXXXX'
  j_password: 's3kr1t'
  redirect:   'https://gss.my.salesforce.com'
sso_cookie_name: 'rh_sso'
cookie_jar_path: 'cookiejar'
'''

import BeautifulSoup
import requests
from requests.packages.urllib3.connectionpool import InsecureRequestWarning
import requests.auth
from requests.cookies import extract_cookies_to_jar
import re
import os
import sys
import warnings
import yaml
from cookielib import LWPCookieJar


# pylint: disable=too-few-public-methods
class SAMLAuth(requests.auth.AuthBase):
    '''
    This class attempts to get an SSO cookie by submitting credentials and
    following redirects, posting form data as necessary
    '''

    def __init__(self, session):
        # This points back to the parent session
        self.session = session

    def handle_auth(self, response, **kwargs):
        '''Takes the given response and tries SAML auth, if needed.'''

        if response.status_code not in [401, 403]:
            return response

        # Consume content and release the original connection
        # to allow our new request to reuse the same one.
        response.content # pylint: disable=pointless-statement
        response.raw.release_conn()
        prep = response.request.copy()

        # PreparedResponse does not have a method to get _cookies.
        # This is reuse of code from python requests.auth
        # pylint: disable=protected-access
        extract_cookies_to_jar(prep._cookies, response.request, response.raw)

        self.session.auth = None
        self.session.get_sso_cookie()
        self.session.auth = self

        prep.prepare_cookies(self.session.cookies)

        new_response = response.connection.send(prep, **kwargs)
        new_response.history.append(response)
        new_response.request = prep

        return new_response

    def __call__(self, r):
        r.register_hook('response', self.handle_auth)
        return r

class SAMLAuthSession(requests.sessions.Session):
    '''
    This is a special subclass of Session which allows us to get an SSO cookie
    with the SAMLAuth class and store it both on disk and in our session.
    '''

    def __init__(self, **kwargs):
        self.cfg = kwargs.get('cfg', {})
        super(SAMLAuthSession, self).__init__()
        self.auth = SAMLAuth(self)
        if self.cfg['cookie_jar_path'] is not None:
            self.initialize_cookie_jar()
        warnings.simplefilter("ignore", InsecureRequestWarning)

    def initialize_cookie_jar(self):
        """Load cookies from disk, creating a new file if needed."""
        self.cookies = LWPCookieJar(self.cfg['cookie_jar_path'])
        if not os.path.exists('cookiejar'):
            # Create a new cookies file and set our Session's cookies
            self.cookies.save()
        self.cookies.load(ignore_discard=True)

    def get_sso_cookie(self):
        """Post credentials and follow redirects until we have a cookie."""
        cookie_dict = requests.utils.dict_from_cookiejar(self.cookies)
        # ARG: check for expired cookies, since we are doing ignore_discard=True
        if self.cfg['sso_cookie_name'] not in cookie_dict.keys():
            # This request gets us some initial cookies like JSESSION
            # I have no idea what the generalized form of this should be.
            # Maybe instead of initializing with username/password, I should
            # actually be taking a params dict.
            response = self.get(self.cfg['idp_url'],
                                params=self.cfg['auth_params'])
            print response.status_code

            # Request protected resource from Service Provider (SP)
            response2 = self.get(self.cfg['sp_url'])
            # Post SAML AuthN to Identity Provider (IdP)
            response3 = self.parse_and_post_form(response2.text)
            # Post SAML Assertion to SP
            response4 = self.parse_and_post_form(response3.text)
            # ... and one more redirect?
            response5 = self.parse_and_post_form(response4.text)
            if response5.status_code != 200:
                # ARG: Check all the http statuses and error if we don't get the
                # SSO cookie here.
                sys.stderr.write('WARNING: final SSO page load failed.')
                sys.stderr.flush()

            self.cookies.save(ignore_discard=True)

    def parse_and_post_form(self, htmldata):
        """Parse a pre-filled form and post it (for SAML conversations)."""
        dom = BeautifulSoup.BeautifulSoup(htmldata)
        form = dom.find("form")
        params = {}
        for input_field in form.findAll("input", \
                {'type': re.compile('hidden', re.IGNORECASE)}):
            params[input_field['name']] = input_field['value']

        return self.post(form['action'], data=params)

def main():
    '''Example code for demonstration purposes.'''
    config = yaml.load(open('saml_auth.yaml').read())
    sso_session = SAMLAuthSession(cfg=config)
    resp = sso_session.get(config['test_url'], verify=False)
    print resp.text
    sso_session.cookies.save(ignore_discard=True)

if __name__ == "__main__":
    main()
