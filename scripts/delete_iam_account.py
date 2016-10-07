#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script can be used to create API keys for your AWS IAM user accounts.
 It can be used for individual accounts or for all your accounts at once.

 Note: we have a limit of 2 access keys per user, so by default this will delete the old ones

 Usage:

 For individual accounts:
 aws_api_key_manager.py -p ded-stage-aws -p ded-int-aws -p <some-other-account>


 For all accounts found in /etc/openshift_tools/aws_accounts.txt:
 aws_api_key_manager.py --all

 To manage keys for another user, use the '-u' option:
 aws_api_key_manager.py -u <some-other-user> -p ded-stage-aws
"""

from __future__ import print_function

import argparse
import os
import pwd
import sys
import yaml

# pylint: disable=import-error
import boto3
import botocore

import saml_aws_creds


class DeleteUser(object):
    ''' class to delete an iam user from ops acounts'''


    def __init__(self):
        """ constructor """
        self.response = None


    @staticmethod
    def check_arguments():
        """ ensure that an argument was passed in from the command line """

        parser = argparse.ArgumentParser(description='Manage API keys for IAM accounts')
        parser.add_argument("-a", "--all",
                            help="manage API keys for every profile in ~/.aws/credentials",
                            action="store_true")
        parser.add_argument("-p", "--profile",
                            help="manage API keys for the specified profile",
                            action='append')
        parser.add_argument("-u", "--user",
                            help="specify a username for the account")
        args = parser.parse_args()

        if not args.all and not args.profile:
            print('Specify an account ID or profile name. \
            To change the password for all accounts on file, use \"--all\"')
            print('Usage:')
            print('example: %s <account-id-number>' % parser.prog)
            print('example: %s --all' % parser.prog)
            sys.exit(10)
        else:
            if args.user != 'root':
                return args


    @staticmethod
    def get_ops_accounts():
        ''' retrieve the config-managed list of ops AWS accounts '''

        path = '/etc/openshift_tools/aws_accounts.txt'
        accounts_list = []

        if os.path.isfile(path):
            with open(path) as open_file:
                stripped_line = list([line.rstrip() for line in open_file.readlines()])
                for line in stripped_line:
                    if line is not None:
                        accounts_list.append(line)
                return accounts_list
        else:
            raise ValueError(path + 'does not exist')


    @staticmethod
    def delete_user(user_name, client):
        """ create an iam user account """

        client.remove_user_from_group(GroupName='admin', UserName=user_name)

        response = client.delete_user(
            UserName=user_name
            )

        return response


    def check_user(self, aws_account, user_name, client):
        """ check if the user exists locally and in aws. deletes iam user if found """

        try:
            client.get_user(UserName=user_name)
        except botocore.exceptions.ClientError as client_exception:
            if client_exception.response['Error']['Code'] == 'NoSuchEntity':
                return True

        else:
            system_users = []

            for user in pwd.getpwall():
                system_users.append(user[0])

            if user_name in system_users and user_name != 'root' and os.getegid() < 1000:
                print("Found existing IAM account in %s, \
                deleting IAM account for user %s" % (aws_account, user_name))

                response = self.delete_user(user_name, client)

                return response
            else:
                print('can\'t delete this user')


    @staticmethod
    def get_keys(user_name, client):
        """ get the Access Key IDs of any API keys the user has and return the oldest key"""

        existing_keys = client.list_access_keys(
            UserName=user_name)

        all_keys = existing_keys['AccessKeyMetadata']
        keys_list = []

        if all_keys:
            for ekey in all_keys:
                keys_list.append(ekey['AccessKeyId'])

        return keys_list


    @staticmethod
    def delete_key(aws_account, user_name, key, client):
        """ delete an API key for the specified account"""

        response = client.delete_access_key(
            UserName=user_name,
            AccessKeyId=key
            )

        print('found and deleted api key for:', aws_account)
        return response


    @staticmethod
    def get_token(aws_account):
        """ generate temporary SSO access credentials  """

        sso_config_path = '/etc/openshift_tools/sso-config.yaml'

        if os.path.isfile(sso_config_path):
            with open(sso_config_path, 'r') as sso_config:
                yaml_config = yaml.load(sso_config)

                if yaml_config["idp_host"]:
                    ops_idp_host = yaml_config["idp_host"]

                creds = saml_aws_creds.get_temp_credentials(
                    metadata_id='urn:amazon:webservices:%s' % aws_account,
                    idp_host=ops_idp_host
                    )

                client = boto3.client(
                    'iam',
                    aws_access_key_id=creds['AccessKeyId'],
                    aws_secret_access_key=creds['SecretAccessKey'],
                    aws_session_token=creds['SessionToken']
                    )

                return client

        else:
            raise ValueError(sso_config_path + 'does not exist')


    def main(self):
        ''' main function '''
        args = self.check_arguments()
        ops_accounts = self.get_ops_accounts()

        if args.profile and args.user:

            for aws_account in args.profile:
                matching = [s for s in ops_accounts if aws_account in s]
                account_name = matching[0].split(':')[1]
                client = self.get_token(account_name)
                existing_keys = self.get_keys(args.user, client)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)

                self.check_user(aws_account, args.user, client)

        elif args.all and args.user:

            for aws_account in ops_accounts:
                client = self.get_token(aws_account)

                existing_keys = self.get_keys(args.user, client)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)

                self.check_user(aws_account, args.user, client)

        else:
            raise ValueError('No suitable arguments provided')


if __name__ == '__main__':
    DELETE = DeleteUser()
    DELETE.main()
