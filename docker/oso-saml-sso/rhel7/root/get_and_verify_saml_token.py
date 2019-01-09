#!/usr/bin/env python2
#
# This is a helper script for "get_saml_token" provided with SimpleSaml.
#
# Whereas "get_saml_token" generates HTML data and returns it to the user
# (at which point they do HTML/XML manipulation to extract an AWS CLI key)
# this wrapper script does that same logic internally, then uses the key
# to verify itself, and if it passes the original content is returned, same
# as before.
#
# This appears convoluted but means it inter-operates identically to the
# get_saml_token version, except with internal filtering added.
#
# CONDITIONS:
# - It assumes IAM users/groups are global.
# - It assumes that same-named GROUPS and ROLES are equivalent.
# - It assumes that assumed usernames match actual IAM usernames.
#
# With these two assumptions, we allow for the per-account IAM user config
# to act as a finer grained permission control on STS requests to avoid
# copying that configuration into the SSO container.
#
#
# TESTING (inside container):
# - cd /usr/local/bin/
# - export SSH_ORIGINAL_COMMAND=urn:amazon:webservices:123456789012
# - ./get_saml_token user@example.com            <-- return SAML token
# - ./get_and_verify_saml_token user@example.com <-- return token if valid
#
#
# USAGE:
# - To use the regular method, add this to authorized_keys.  The email
#   address is probably also added to the default admin group, and can
#   leverage the SSO pod either by web (OAuth) authentication by the same
#   email address, or via ssh access where the email is directly linked to
#   the ssh key.
#     command="get_saml_token user@example.com" ssh-rsa AAAA....
#
# - To use this new method, add this to authorized_keys instead.  The
#   @ssh-only indicates it's only valid for ssh access (ineligible for 
#   OAuth), and the ..._and_verify_... command runs this script to filter
#   results before they are returned to the calling user.
#     command="get_saml_token user@ssh-only" ssh-rsa AAAA....
#
#
# IAM USERS AND GROUPS:
# - If the SAML assertion creates a something like:
#   "Arn": "arn:aws:sts::123456789012:assumed-role/admin/username"
#
# - We check that the IAM user "username" exists in the given account
# - We check that the IAM user belongs to a group named "admin" in the
#   given account
# - Only if both these pass, the SAML assertion is returned.
#
# - Ergo, to enable/disable access, create/delete the named user, or
#   add/remove them from the groups desired per account.
#
#
#
# REVISION HISTORY
#
#   2016         Joel Smith    Original script to parse SAML token to IAM keys
#   2019-01-04   Dave Baker    Proof of Concept to filter by IAM
#   2019-01-08   Dave Baker    Script integrated for use
#
#

import os
import sys
import subprocess
import re
import boto3
import bs4
import base64
import xml.etree.ElementTree as ET


# Step 0
# - crude input validation

if len(sys.argv) != 2:
  raise ValueError("Usage: $0 email-address")

if not os.environ.get('SSH_ORIGINAL_COMMAND'):
  raise ValueError("SSH_ORIGINAL_COMMAND must be defined")



# Step 1 
# - run get_saml_token passing through our first argument (plus env)
# - capture HTML output for processing (and later display)

cmd = subprocess.Popen([ "/usr/local/bin/get_saml_token", sys.argv[1] ],
      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

html_saml, cmd_error = cmd.communicate()

if cmd.returncode != 0:
  raise ValueError("Error connecting to SAML IdP:\nSTDERR:\n" + cmd_error)



# Step 2
# - turn HTML saml assertion into API keys
# - (this is in great part copied from saml_aws_creds)

assertion = None
soup = bs4.BeautifulSoup(html_saml)

# look for SAMLResponse attribute
for inputtag in soup.find_all('input'):
  if inputtag.get('name') == 'SAMLResponse':
    assertion = inputtag.get('value')

if not assertion:
  raise ValueError("Error retrieving SAML token from SSO pod")


# Use the SAML assertion to assume_role_with_saml()

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
    raise ValueError("No Credentials returned within SAML assertion")




## DEBUG
##
## print '# GOT api keys ... pending validation'
## print 'AWS_ACCESS_KEY_ID="{}"'.format( response['Credentials']['AccessKeyId'])
##



# Step 3
# - create boto client with those keys to self-validate

try:
  sts = boto3.client('sts', 
          aws_access_key_id=     response['Credentials']['AccessKeyId'],
          aws_secret_access_key= response['Credentials']['SecretAccessKey'],
          aws_session_token=     response['Credentials']['SessionToken']
        ).get_caller_identity()
except:
  raise ValueError("Could not perform get-caller-identity.  Invalid creds?")
  

# For a STS key, we'll get something like this (arn:aws:sts ...) in which
# case we extract the assumed role and user to further validate
#     "Arn": "arn:aws:sts::639866565627:assumed-role/admin/serviceacct"
#
# If we get something else (e.g. a regular IAM user will return something like
# "Arn": "arn:aws:iam::980499179201:user/someuser") then we return failure since
# this is unexpected.


match = re.search('^arn:aws:sts.*?:assumed-role/(\w+)/(\w+)$', sts['Arn'])

if not match:
  raise ValueError("ARN did not match arn:aws:sts format.")


else:
  assumedrole = match.group(1)
  assumeduser = match.group(2)

  print "# Matched STS token for assumed role " + assumedrole + " with username " + assumeduser

  # "List Groups for User" will both confirm if the user exists, and
  # what groups it's a member of
  try:
    lgfu = boto3.client('iam',
           aws_access_key_id=     response['Credentials']['AccessKeyId'],
           aws_secret_access_key= response['Credentials']['SecretAccessKey'],
           aws_session_token=     response['Credentials']['SessionToken']
           ).list_groups_for_user(UserName = assumeduser)
  except:
    raise ValueError("IAM user look up failed - no such user?")




  # match all groups against the assumed role
  matches = [ element for element in lgfu['Groups'] if element['GroupName'] == assumedrole ]

  if len(matches) < 1:
    raise ValueError("Assumed role not in valid groups for this user")
  



# If all our testing succeeded, we pass through the original HTML output
# to be processed by the calling script.

print html_saml




# debug / optional - also print the contents of the API key we generated
# print "<!-- SAML Assertion included above was used to create this API key: "
# print 'AWS_ACCESS_KEY_ID="{}"'.format( response['Credentials']['AccessKeyId'] )
# print 'AWS_SECRET_ACCESS_KEY="{}"'.format( response['Credentials']['SecretAccessKey'] )
# print 'AWS_SESSION_TOKEN="{}"'.format( response['Credentials']['SessionToken'] )
# print "-->"


