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
import ConfigParser
import getpass
import os
import pwd
import re
import sys
import time
import yaml

# pylint: disable=import-error
import boto3
import botocore

import saml_aws_creds


class ManageKeys(object):
    """ class to create and update IAM user account API keys """


    def __init__(self):
        """ constructor """
        self.response = None


    @staticmethod
    def check_arguments():
        """ ensure that an argument was passed in from the command line """

        parser = argparse.ArgumentParser(description='Create API keys for IAM accounts')
        parser.add_argument("-a", "--all",
                            help="create API keys for every ops aws account",
                            action="store_true")
        parser.add_argument("-p", "--profile",
                            help="create new API keys for the specified profile",
                            action='append')
        parser.add_argument("-u", "--user",
                            help="specify a username for the account")
        args = parser.parse_args()

        if not args.all and not args.profile:
            print('Specify an account ID or profile name. \
            To generate the keys for all ops accounts, use \"--all\"')
            print('Usage:')
            print('example: %s <account-id-number>' % parser.prog)
            print('example: %s --all' % parser.prog)
            sys.exit(10)
        else:
            if args.user is None:
                if getpass.getuser() != 'root' and os.getegid() < 1000:
                    args.user = getpass.getuser()
            return args


    @staticmethod
    def check_accounts():
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
            raise ValueError(path + ' does not exist')


    def check_user(self, aws_account, user_name, client):
        """ check if the user exists locally and in aws. creates iam user if not found """

        try:
            client.get_user(UserName=user_name)
        except botocore.exceptions.ClientError as client_exception:
            if client_exception.response['Error']['Code'] == 'NoSuchEntity':
                system_users = []

                for user in pwd.getpwall():
                    system_users.append(user[0])

                if user_name in system_users and user_name != 'root' and os.getegid() < 1000:
                    print("User does not have an existing IAM account for %s, \
                    creating  new account for user %s" % (aws_account, user_name))

                response = self.create_user(aws_account, user_name, client)

                return response
            else:
                return True


    @staticmethod
    def create_user(aws_account, user_name, client):
        """ create an iam user account """

        response = client.create_user(
            UserName=user_name
            )

        client.add_user_to_group(GroupName='admin', UserName=user_name)
        print('A new user account was added.\
        Use change_iam_password.py -p %s to set your password' % aws_account)

        return response


    @staticmethod
    def get_all_profiles():
        """ if -a is specified, generate a list of all profiles found in ~/.aws/credentials """

        path = os.path.join(os.path.expanduser('~'), '.aws/credentials')
        profile_list = []

        if os.path.isfile(path):
            with open(path) as open_file:
                stripped_line = list([line.rstrip() for line in open_file.readlines()])
                for line in stripped_line:
                    account = re.match(r"^\[([A-Za-z0-9_\-]+)\]", line)
                    if account is not None:
                        profile_list.append(account.group(1))
                return profile_list
        else:
            raise ValueError(path + ' does not exist')


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

    @staticmethod
    def create_key(aws_account, user_name, client):
        """ change an API key for the specified account"""

        response = client.create_access_key(
            UserName=user_name
            )

        print('key successfully created for:', aws_account)
        return response


    @staticmethod
    def delete_key(aws_account, user_name, key, client):
        """ delete an API key for the specified account"""

        response = client.delete_access_key(
            UserName=user_name,
            AccessKeyId=key
            )

        print('key successfully deleted for:', aws_account)
        return response


    @staticmethod
    def manage_timestamp(update=False):
        """ create or update expiration file """

        path = os.path.join(os.path.expanduser('~'), '.aws/credentials_expiration')
        exp_date = str(int(time.time())+180*24*60*60)

        if os.path.isfile(path) and update is True:
            print('file exists, ready to write')
            with open(path, 'w') as open_file:
                open_file.write(exp_date)

        elif not os.path.isfile(path):
            print('file does not exist, creating')
            with open(path, 'w') as open_file:
                open_file.write(exp_date)

        else:
            print('checked for file and it exists. no write was called. nothing to do here')
            return True


    @staticmethod
    def write_credentials(aws_account, key_object):
        ''' write the profile for the user account to the AWS credentials file '''

        path = os.path.join(os.path.expanduser('~'), '.aws/credentials')

        if os.path.isfile(path):
            config = ConfigParser.RawConfigParser()
            config.read(path)

            try:
                config.get(aws_account, 'aws_access_key_id')

            except ConfigParser.NoSectionError:
                config.add_section(aws_account)
                config.set(aws_account, 'aws_access_key_id',\
                                key_object['AccessKey']['AccessKeyId'])
                config.set(aws_account, 'aws_secret_access_key',\
                                key_object['AccessKey']['SecretAccessKey'])

                with open(path, 'w') as configfile:
                    config.write(configfile)

            else:
                config.set(aws_account, 'aws_access_key_id',\
                                key_object['AccessKey']['AccessKeyId'])
                config.set(aws_account, 'aws_secret_access_key',\
                                key_object['AccessKey']['SecretAccessKey'])

                with open(path, 'w') as configfile:
                    config.write(configfile)

        else:
            raise ValueError(path + ' does not exist')


    def main(self):
        """ main function """
        args = self.check_arguments()
        ops_accounts = self.check_accounts()

        if args.profile and args.user:

            for aws_account in args.profile:
                matching = [s for s in ops_accounts if aws_account in s]
                account_name = matching[0].split(':')[1]
                client = self.get_token(account_name)
                self.check_user(aws_account, args.user, client)
                existing_keys = self.get_keys(args.user, client)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)
                        key_object = self.create_key(aws_account, args.user, client)
                        self.write_credentials(aws_account, key_object)

                else:
                    key_object = self.create_key(aws_account, args.user, client)
                    self.write_credentials(aws_account, key_object)

            self.manage_timestamp()

        elif args.all and args.user:

            for aws_account in ops_accounts:
                client = self.get_token(aws_account)
                self.check_user(aws_account, args.user, client)
                current_accounts = self.get_all_profiles()
                existing_keys = self.get_keys(args.user, client)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)

                if aws_account not in current_accounts:
                    key_object = self.create_key(aws_account, args.user, client)
                    self.write_credentials(aws_account, key_object)

            self.manage_timestamp(True)

        else:
            raise ValueError('No suitable arguments provided')


if __name__ == '__main__':
    MANAGE = ManageKeys()
    MANAGE.main()
