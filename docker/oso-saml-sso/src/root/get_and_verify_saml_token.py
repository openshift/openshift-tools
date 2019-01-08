#!/usr/bin/env python2
#
# This is a helper script for "get_saml_token" provided with SimpleSaml.
#
# It calls "get_saml_token" but instead of returning the STS token to the
# user, it uses that same token to verify if the assumed_role details 
# correspond to a valid IAM user.
#
# It assumes that same-named GROUPS and ROLES are equivalent.
# It assumes that assumed usernames match actual IAM usernames.
#
# With these two assumptions, we allow for the per-account IAM user config
# to act as a finer grained permission control on STS requests to avoid
# copying that configuration into the SSO container.
#
#
# REVISION HISTORY
#
#   2019-01-07   Dave Baker    Placeholder file for final script
#


import subprocess
import re
import boto3


# Dummy output
print '# Placeholder script not yet functional'
print 'AWS_ACCESS_KEY_ID="ASI..."'
print 'AWS_SECRET_ACCESS_KEY="......"'
print 'AWS_SESSION_TOKEN="..........................."'

exit(0)

