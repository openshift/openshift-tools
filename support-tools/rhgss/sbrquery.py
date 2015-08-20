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
Purpose: Perform queries through RH "unified" API
'''

import json
import re
import yaml
import samlauth
import argparse

class UnifiedClient(object):
    '''
    This class provides some helper functions for querying SalesForce cases
    via the Unified API.
    '''

    def __init__(self, cfg):
        self.endpoint = cfg['unified_endpoint']
        self.session = samlauth.SAMLAuthSession(cfg=cfg)

    def get_sbr_members(self, sbr_name):
        '''Get possible case owners by SBR membership.'''
        # pylint: disable=line-too-long
        resp = self.session.get('%s/user?where=(sbrName is "%s" or roleSbrName is "%s")' % \
                                (self.endpoint, sbr_name, sbr_name), verify=False)
        data = json.loads(resp.text)
        sbr_ids = [x['externalModelId'] for x in data]
        return sbr_ids

    def get_sbr_cases(self, sbr_name, status=None, internal_status=None,
                      product=None):
        '''
        Get cases owned by members of an SBR, optionally filtering by
        status and product.
        '''
        sbr_members = self.get_sbr_members(sbr_name)
        query = []
        query.append('(ownerId in %s)' % json.dumps(sbr_members))
        if status is not None and len(status):
            query.append('(status in %s or isFTS is true)' % json.dumps(status))
        if internal_status is not None and len(internal_status):
            query.append('(internalStatus in %s)' % json.dumps(internal_status))

        print ' and '.join(query)
        resp = self.session.get('%s/case?where=(%s)' % \
                                (self.endpoint, ' and '.join(query)))
        if len(resp.text) == 0:
            return

        # python 2.x and unicode ... not going to bother right now
        plate = json.loads(re.sub(r'[^\x00-\x7F]', ' ', resp.text))
        if product is None or not len(product):
            return plate

        # pylint: disable=line-too-long
        return [case for case in plate if
                case['resource']['product']['resource']['line']['resource']['name'].lower()
                in product]

def maincli():
    """Parse command-line arguments an run a query."""
    parser = argparse.ArgumentParser(description="query SBR cases")
    parser.add_argument('-c', '--config-file', default='rh_auth.yaml',
                        help='Path to config file')
    parser.add_argument('-t', '--sbr-team',
                        help='SBR team to query')
    parser.add_argument('-s', '--status', action='append',
                        help='case status query param')
    parser.add_argument('-i', '--internal-status', action='append',
                        help='case internal status query param')
    parser.add_argument('-p', '--product', action='append',
                        help='product query param')
    parser.add_argument('-e', '--endpoint',
                        default='https://unified.gsslab.rdu2.redhat.com',
                        help='Unified API endpoint URL')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Unified API endpoint URL')

    # My preferrred defaults
    parser.set_defaults(sbr_team='Shift',
                        status=['Waiting on Red Hat'],
                        internal_status=['Waiting on Collaboration'],
                        product=['OpenShift Online'])
    args = parser.parse_args()
    cfg = yaml.load(open(args.config_file).read())
    cfg['unified_endpoint'] = args.endpoint
    client = UnifiedClient(cfg)
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    cases = client.get_sbr_cases(args.sbr_team, status=args.status,
                                 internal_status=args.internal_status,
                                 product=[x.lower() for x in args.product])

    print json.dumps(cases, indent=4)

if __name__ == "__main__":
    maincli()
