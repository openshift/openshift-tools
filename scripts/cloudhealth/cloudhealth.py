# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.""

'''
These classes interface with the cloudhealth Account API

For more info, see:
https://github.com/CloudHealth/cht_api_guide/blob/master/account_api.md
'''

import json
import logging
import requests

LOG = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class CloudHealthAwsAccountApi(object):
    ''' low-level class for interfacing with CloudHealth AWS Account API '''

    endpoint = 'https://chapi.cloudhealthtech.com/v1/aws_accounts'
    api_key = None
    __total_accounts = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        # pylint: disable=line-too-long
        if not self.api_key:
            raise Exception('Missing parameter "api_key" is required for authentication.')

    def _create(self, **kwargs):
        '''
        create account

        for param details, see:
        https://github.com/CloudHealth/cht_api_guide/blob/master/account_api.md
        '''
        params = {'api_key' : self.api_key}
        headers = {'content-type':'application/json'}
        resp = requests.post(self.endpoint,
                             params=params,
                             headers=headers,
                             json=kwargs)
        if resp.status_code == requests.codes.get('ok'):
            return resp.json()
        else:
            resp.raise_for_status()

    def _read(self, account_id=None, page=0, per_page=100):
        '''
        read accounts, supports pagination

        params:
            account_id: id number,
                returns list of all accounts if account_id=None
            page: page number
            per_page: items per page
        '''
        params = {'api_key':self.api_key}

        if account_id:
            endpoint = '%s/%s' % (self.endpoint, account_id)
        else:
            endpoint = self.endpoint
            params.update({'page':page, 'per_page':per_page})

        resp = requests.get(endpoint,
                            params=params)
        self.__total_accounts = int(resp.headers['X-Total'])

        if resp.status_code == requests.codes.get('ok'):
            return resp.json()
        else:
            resp.raise_for_status()

    def _read_all(self):
        ''' read all accounts, may be resource-intensive '''
        page = 0
        resp = self._read(page=page)
        accounts = resp.get('aws_accounts', [])
        while len(accounts) < self.__total_accounts:
            page += 1
            resp = self._read(page=page)

            # only add non-duplicates to the account list
            #
            # normally, I'd use a tuple here, but the object is nested dicts
            # converting to a tuple doesn't make the nested dicts immutable.
            # so, we dump to a json string, which set() can work with.
            seen = set(json.dumps(acc.items()) for acc in accounts)
            for acc in resp.get('aws_accounts', []):
                if json.dumps(acc.items()) not in seen:
                    accounts.append(acc)
        return accounts

    def _update(self, account_id, **kwargs):
        ''' update existing accounts '''
        params = {'api_key':self.api_key}
        headers = {'content-type':'application/json'}
        resp = requests.put('%s/%s' % (self.endpoint, account_id),
                            params=params,
                            headers=headers,
                            json=kwargs)
        if resp.status_code == requests.codes.get('ok'):
            return resp.json()
        else:
            resp.raise_for_status()

    def _delete(self, account_id=None):
        ''' delete accounts '''
        params = {'api_key':self.api_key}
        resp = requests.get('%s/%s' % (self.endpoint, account_id),
                            params=params)
        if resp.status_code == requests.codes.get('ok'):
            return resp.json()
        else:
            resp.raise_for_status()

class CloudHealthAwsAccount(CloudHealthAwsAccountApi):
    ''' class for accessing a CloudHealth AWS Account object '''
    # pylint: disable=invalid-name
    id = None
    owner_id = None
    amazon_name = None
    authentication = {
        #"protocol": None,
        #"access_key": None,
        #"secret_key": None,
        #"assume_role_arn" : None,
        #"assume_role_external_id" : None,
    }
    aws_config = {
        #"enabled" : False,
        #"bucket": None,
        #"prefix": None
    }
    billing = {
        #"bucket": None
    }
    cloudtrail = {
        #"enabled": False,
        #"bucket": None
    }
    name = None
    tags = [
        #{'key':None, 'value':None}
    ]

    def __init__(self, **kwargs):
        super(CloudHealthAwsAccount, self).__init__(**kwargs)

        if self.name or self.owner_id:
            self._load()
        else:
            raise Exception('Missing required parameter "name".')

        # pylint: disable=line-too-long
        if 'authentication' in kwargs.keys() and \
                'protocol' in kwargs['authentication'].keys():
            if kwargs['authentication']['protocol'] not in ['access_key', 'assume_role']:
                raise Exception('Protocol must be one of "access_key" or "assume_role"')

            if kwargs['authentication']['protocol'] == 'access_key':
                if not kwargs['authentication'].get('access_key', None) or \
                        not kwargs['authentication'].get('secret_key', None):
                    raise Exception('Missing values for "access_key" or "secret_key"')

            if kwargs['authentication']['protocol'] == 'assume_role':
                if not kwargs['authentication'].get('assume_role_arn', None):
                    raise Exception('Missing values for "assume_role_arn"')

    def __repr__(self):
        return str(self.__dict__)

    def _load(self):
        ''' load info based on account name '''
        for account in self._read_all():
            # pylint: disable=line-too-long
            if (self.name and self.name == account.get('amazon_name')) \
            or (self.owner_id and str(self.owner_id) == account.get('owner_id')):
                for key, value in account.items():
                    setattr(self, key, value)
                return

    def delete(self):
        ''' deletes this account '''
        return super(CloudHealthAwsAccount, self)._delete(self.id)

    def read(self):
        ''' reads this account '''
        return super(CloudHealthAwsAccount, self)._read(self.id)

    def _get_params(self):
        ''' compile params for create/update methods '''
        params = {'name' : self.name,
                  'authentication' : self.authentication}

        if self.authentication.get("assume_role_arn", None) and \
                not self.authentication.get("assume_role_external_id", None):
            params['authentication']['assume_role_external_id'] = self.generate_external_id()

        if len(self.billing) > 0:
            params.update({'billing' : self.billing})
        if len(self.cloudtrail) > 0:
            params.update({'cloudtrail' : self.cloudtrail})
        if len(self.aws_config) > 0:
            params.update({'aws_config' : self.aws_config})
        if len(self.tags) > 0:
            params.update({'tags' : self.tags})

        return params

    def create(self):
        ''' creates this account '''
        params = self._get_params()

        # pylint: disable=star-args
        return super(CloudHealthAwsAccount, self)._create(**params)

    def update(self):
        ''' updates this account '''
        params = self._get_params()

        # pylint: disable=star-args
        return super(CloudHealthAwsAccount, self)._update(self.id, **params)

    def generate_external_id(self):
        ''' generate an external ID '''
        params = {'api_key':self.api_key}
        headers = {'content-type':'application/json'}
        resp = requests.get('%s/%s/generate_external_id' % \
                            (self.endpoint, self.id),
                            params=params,
                            headers=headers)
        if resp.status_code == requests.codes.get('ok'):
            obj = resp.json()
            return obj['generated_external_id']
        else:
            resp.raise_for_status()
