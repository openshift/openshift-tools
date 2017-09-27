#!/usr/bin/env python
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
This script adds a role to AWS accounts to enable access from cloudhealth
'''

from ConfigParser import ConfigParser

import argparse
import json
import logging
import os
import sys

import boto3
import botocore.exceptions
import requests.exceptions

from cloudhealth import CloudHealthAwsAccount

LOG_FORMAT = '%(asctime)-15s [%(levelname)s] (%(name)s.%(funcName)s) %(message)s'

def setup_logging(level=logging.NOTSET):
    ''' configure logging'''
    logging.basicConfig(format=LOG_FORMAT, level=level)
    log = logging.getLogger(__name__)
    return log

def parse_args():
    ''' parse CLI args '''
    parser = argparse.ArgumentParser(description='MY SCRIPT DESCRIPTION')
    parser.add_argument('-e', '--external-id', type=str, dest='aws_external_id',
                        help="External ID String for AWS cross-account trust")
    parser.add_argument('-f', '--file', type=str, dest='credsfile',
                        default='%s/.aws/credentials' % os.environ['HOME'],
                        help='aws credentials file')
    parser.add_argument('-k', '--cloudhealth-key', type=str, dest='cht_api_key',
                        help="The API Key for CloudHealth")
    parser.add_argument('-n', '--role-name', type=str, dest='aws_role_name',
                        default='default',
                        help="The name used for the AWS Role and Policy. Must match permissions file name, too.")
    parser.add_argument('-p', '--profile', type=str,
                        help="The profile name for the AWS account")
    parser.add_argument('-r', '--region', type=str, default='us-east-1',
                        help='AWS region, default: us-east-1')
    parser.add_argument('-v', action='count', dest='verbose',
                        help='verbosity. up to -vvv supported.')

    args = parser.parse_args()
    return args

def get_account_number():
    ''' get AWS Account number from STS '''
    session = boto3.Session(profile_name=os.environ['AWS_PROFILE'])
    sts = session.client('sts')
    query = sts.get_caller_identity()
    return query['Account']

def setup_role_policy(account_number, name='default'):
    ''' create the role and policy in AWS '''

    policy_document = load_json('%s.json' % name)
    policy_arn = 'arn:aws:iam::%s:policy/%s' % (account_number, name)

    session = boto3.Session(profile_name=os.environ['AWS_PROFILE'])
    iam = session.client('iam')

    # putting the "Allow read-only S3" permissions here to allow us to do string
    # interpolation on them.
    read_s3_policy_arn = 'arn:aws:iam::%s:policy/read_s3_%s' % (account_number,
                                                                name)
    read_s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:Get*",
                    "s3:List*"
                ],
                "Resource": [
                    "arn:aws:s3:::%s" % name,
                    "arn:aws:s3:::%s/*" % name
                ]
            }
        ]
    }

    check_create(conn=iam,
                 check_func='get_role',
                 check_args={'RoleName':name},
                 create_func='create_role',
                 create_args={'RoleName':name,
                              'AssumeRolePolicyDocument':json.dumps(
                                  policy_document)})

    check_create(conn=iam,
                 check_func='get_policy',
                 check_args={'PolicyArn':policy_arn},
                 create_func='create_policy',
                 create_args={'PolicyName':name,
                              'PolicyDocument':json.dumps(policy_document)})

    check_create(conn=iam,
                 check_func='get_policy',
                 check_args={'PolicyArn':read_s3_policy_arn},
                 create_func='create_policy',
                 create_args={'PolicyName':"read_s3_%s" % name,
                              'PolicyDocument':json.dumps(read_s3_policy)})

    check_create(conn=iam,
                 check_func='get_role_policy',
                 check_args={'RoleName':name, 'PolicyName':name},
                 create_func='attach_role_policy',
                 create_args={'RoleName':name, 'PolicyArn':policy_arn})

    check_create(conn=iam,
                 check_func='get_role_policy',
                 check_args={'RoleName':name, 'PolicyName':"read_s3_%s" % name},
                 create_func='attach_role_policy',
                 create_args={'RoleName':name,
                              'PolicyArn':read_s3_policy_arn})

def check_create(**kwargs):
    ''' check for an AWS object, then create the object if it doesn't exist '''
    # pylint: disable=star-args
    check = None
    try:
        check = getattr(kwargs['conn'],
                        kwargs['check_func'])(**kwargs['check_args'])
        LOG.info(check)
    except botocore.exceptions.ClientError as exc:
        LOG.debug(exc.message)

    if not check:
        resp = getattr(kwargs['conn'],
                       kwargs['create_func'])(**kwargs['create_args'])
        LOG.info(resp)
        LOG.warn('AWS %s completed.', kwargs['create_func'])
    else:
        LOG.warn('AWS %s found a valid object. Skipping creation.',
                 kwargs['check_func'])


def setup_cloudhealth_account(api_key, account_number, external_id=None):
    ''' create an account listing in cloudhealth '''
    cht = CloudHealthAwsAccount(api_key=api_key,
                                owner_id=u'%s' % str(account_number))
    LOG.info('CloudHealth Account: %s', cht)
    # pylint: disable=line-too-long
    if not getattr(cht, 'id', None):
        cht.authentication = {'assume_role_external_id': external_id,
                              'protocol': 'assume_role',
                              'assume_role_arn': 'arn:aws:iam::%s:role/%s ' % \
                                    (str(account_number), ARGS.aws_role_name)}
        cht.name = "%s (%s)" % (os.environ['AWS_PROFILE'], account_number)
        try:
            resp = cht.create()
            LOG.debug('CHT Response: %s', resp)
            LOG.warn('CloudHealth Account created.')
        except requests.exceptions.HTTPError as exc:
            LOG.error('CloudHealth Account create FAILED: %s', exc.message)
    elif cht.authentication.get('assume_role_external_id', None) != external_id:
        cht.authentication = {'assume_role_external_id': external_id,
                              'protocol': 'assume_role',
                              'assume_role_arn': 'arn:aws:iam::%s:role/%s' % \
                                    (str(account_number), ARGS.aws_role_name)}
        try:
            resp = cht.update()
            LOG.debug('CHT Response: %s', resp)
            LOG.warn('CloudHealth Account updated.')
        except requests.exceptions.HTTPError as exc:
            LOG.error('CloudHealth Account update FAILED: %s', exc.message)
    else:
        LOG.warn('CloudHealth Account already exists. Skipping creation.')

def load_json(filename):
    ''' load json file '''
    loadedjson = None
    try:
        with open(filename) as openfile:
            loadedjson = json.load(openfile)
    except TypeError:
        loadedjson = json.load(filename)
    except IOError:
        loadedjson = json.loads('{}')
    except ValueError:
        LOG.error('Unable to read %s', filename)
    return loadedjson

def main():
    ''' main function '''

    # pylint: disable=line-too-long
    if ARGS.cht_api_key:
        api_key = ARGS.cht_api_key
    elif os.environ.get('CLOUDHEALTH_API_KEY', None):
        api_key = os.environ.get('CLOUDHEALTH_API_KEY', None)
    else:
        LOG.error('CloudHealth API Key missing. Use -k or set CLOUDHEALTH_API_KEY in your environment.')
        sys.exit(1)

    if ARGS.profile:
        if not os.environ.get('AWS_PROFILE', None):
            LOG.warn('AWS_PROFILE environment variable not set. Trying profile value.')
            os.environ['AWS_PROFILE'] = ARGS.profile
        account_number = get_account_number()
        LOG.info('using AWS Account: %s', account_number)
        setup_role_policy(account_number, name=ARGS.aws_role_name)
        setup_cloudhealth_account(api_key, account_number)
    else:
        LOG.warn('No profile specified. Looping through all profiles in credentials file.')
        awscreds = ConfigParser()
        awscreds.read(ARGS.credsfile)
        for sect in awscreds.sections():
            LOG.warn('refreshing profile: %s', sect)
            os.environ['AWS_PROFILE'] = sect
            account_number = get_account_number()
            LOG.info('using AWS Account: %s', account_number)
            setup_role_policy(account_number, name=ARGS.name)
            setup_cloudhealth_account(api_key, account_number)

if '__main__' in __name__:
    ARGS = parse_args()

    LEVEL = logging.ERROR
    if ARGS.verbose == 1:
        LEVEL = logging.WARN
    elif ARGS.verbose == 2:
        LEVEL = logging.INFO
    elif ARGS.verbose >= 3:
        LEVEL = logging.DEBUG

    LOG = setup_logging(level=LEVEL)
    try:
        LOG.debug('CLI opts: %s', ARGS)
        main()
    except KeyboardInterrupt:
        LOG.warn("Ctrl-C caught. Exiting...")
        sys.exit(0)
