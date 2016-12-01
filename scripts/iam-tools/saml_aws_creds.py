#!/usr/bin/python

# vim: expandtab:tabstop=4:shiftwidth=4

#   Copyright 2016 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#  Author: Joel Smith <joelsmith@redhat.com>

"""Module for fetching SAML credentials and translating them to API keys"""

from __future__ import print_function
import sys
import subprocess
import base64
import xml.etree.ElementTree as ET

# pylint: disable=import-error
import boto3
from bs4 import BeautifulSoup

def get_temp_credentials(metadata_id, idp_host):
    """
    Use SAML SSO to get a set of credentials that can be used for API access to an AWS account.

    Example:
      import saml_aws_creds
      creds = saml_aws_creds.get_temp_credentials(
          metadata_id='urn:amazon:webservices:123456789012',
          idp_host='login.saml.example.com')

      client = boto3.client(
          'iam',
          aws_access_key_id=creds['AccessKeyId'],
          aws_secret_access_key=creds['SecretAccessKey'],
          aws_session_token=creds['SessionToken'],
          )
    """

    # This SSH command connects to the single-purpose SSH service
    # running on idp_host for the purpose of retrieving a SAML
    # token for the user whose key was used to authenticate.
    # The SSH service on idp_host is expected to be listening
    # only on 127.0.0.1:2222, so the SSH traffic is tunneled
    # through an HTTPS session to idp_host:443.
    ssh = subprocess.Popen(
        (r'''ssh -p 2222 -a \
                 -o "ProxyCommand=bash -c \"exec openssl s_client -servername %h -connect %h:443 -quiet 2>/dev/null \
                                          < <(echo -e 'CONNECT 127.0.0.1:%p HTTP/1.1\\nHost: %h:443\\n'; cat -)\"" \
                 -l {0} {1} {2}''').format('user', idp_host, metadata_id),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        )
    html_saml_assertion, ssh_error = ssh.communicate()
    if ssh.returncode != 0:
        raise ValueError("Error connecting to SAML IdP:\nSTDERR:\n" + ssh_error)

    # Decode the response and extract the SAML assertion
    assertion = None
    soup = BeautifulSoup(html_saml_assertion)

    # Look for the SAMLResponse attribute of the input tag
    for inputtag in soup.find_all('input'):
        if inputtag.get('name') == 'SAMLResponse':
            assertion = inputtag.get('value')

    if not assertion:
        error_msg = soup.find('div', {'id': 'content'})
        if error_msg:
            error_msg = error_msg.get_text()
        else:
            error_msg = html_saml_assertion

        raise ValueError("Error retrieving SAML token: " + error_msg)

    role = None
    principal = None
    xmlroot = ET.fromstring(base64.b64decode(assertion))
    for saml2attribute in xmlroot.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        if saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role':
            for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                role, principal = saml2attributevalue.text.split(',')

    # No API key creds needed since assume_role_with_saml() passes in its own SAML creds instead
    client = boto3.client('sts')
    response = client.assume_role_with_saml(RoleArn=role,
                                            PrincipalArn=principal,
                                            SAMLAssertion=assertion)
    if not response['Credentials']:
        raise ValueError("No Credentials returned")

    return response['Credentials']

def main(argv):
    """Get temporary API keys from SAML SSO credentials"""
    if len(argv) < 3:
        print(('Usage: {0} <metadata_id> <idp_host>\n'
               'Example: {0} urn:amazon:webservices:123456789012 login.saml.example.com\n'
               'To add credentials to your current shell environment:\n'
               '    . <({0} urn:amazon:webservices:123456789012 login.saml.example.com)\n'
               '    export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN').format(argv[0]))
        sys.exit(1)

    creds = get_temp_credentials(metadata_id=argv[1], idp_host=argv[2])

    print('AWS_ACCESS_KEY_ID="{}"'.format(creds['AccessKeyId']))
    print('AWS_SECRET_ACCESS_KEY="{}"'.format(creds['SecretAccessKey']))
    print('AWS_SESSION_TOKEN="{}"'.format(creds['SessionToken']))

if __name__ == '__main__':
    main(sys.argv)
