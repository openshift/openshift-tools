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
    """ Class to create and update IAM user account API keys. """


    def __init__(self):
        """ constructor """
        self.response = None


    @staticmethod
    def check_arguments():
        """ Ensure that an argument was passed in from the command line.

        Returns:
            Parsed argument(s), if provided
        """

        parser = argparse.ArgumentParser(description='Create API keys for IAM accounts.')
        parser.add_argument('-a', '--all',
                            help='Create API keys for every ops aws account.',
                            action='store_true')
        parser.add_argument('-p', '--profile',
                            help='Create new API keys for the specified profile.',
                            action='append')
        parser.add_argument('-u', '--user',
                            help='Specify a username for the account.')
        args = parser.parse_args()

        if not args.all and not args.profile:
            print('Specify an account ID or profile name.\n'
                  'To generate the keys for all ops accounts, use "--all"\n'
                  'Usage:\n'
                  'example: {0} -p <account-name>\n'
                  'example: {0} -u <some-other-user> -p <account-name>\n'
                  'example: {0} --all'.format(parser.prog))
            sys.exit(10)

        if not args.user:
            if getpass.getuser() != 'root' and os.getegid() < 1000:
                args.user = getpass.getuser()
        return args


    @staticmethod
    def check_accounts():
        """ Retrieves a list of the config-managed ops AWS accounts.

        Returns:
            A list containing each of the lines found in the aws accounts file

        Raises:
            A ValueError if the path does not exist
        """

        config_path = '/etc/openshift_tools/sso-config.yaml'
        if os.path.isfile(config_path):
            with open(config_path, 'r') as sso_config:
                yaml_config = yaml.load(sso_config)

                if yaml_config["aws_account_file"]:
                    path = yaml_config["aws_account_file"]

        accounts_list = []

        if os.path.isfile(path):
            with open(path) as open_file:
                stripped_line = list([line.rstrip() for line in open_file.readlines()])
                for line in stripped_line:
                    if line is not None:
                        accounts_list.append(line)
                return accounts_list
        else:
            raise ValueError(path + ' does not exist.')


    def check_user(self, aws_account, user_name, client):
        """ Check if the user exists locally and in aws. creates iam user if not found.

        Returns:
            True, after checking if the IAM user exists in the specified AWS account
            and creating a user account for them if one does not already exist
        """

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

                self.create_user(aws_account, user_name, client)

        return True


    @staticmethod
    def create_user(aws_account, user_name, client):
        """ Create an IAM user account. """

        client.create_user(
            UserName=user_name
            )

        client.add_user_to_group(GroupName='admin', UserName=user_name)
        print("A new user account was added.\n"
              "Use change_iam_password.py -p %s to set your password" % aws_account.split(':')[0])

        return True


    @staticmethod
    def get_all_profiles():
        """ If -a is specified, generate a list of all profiles found in ~/.aws/credentials.

        Returns
            Each profile from the credentials file, stored in a list.

        Raises:
            A ValueError if path is does not exist.
        """

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
            raise ValueError(path + ' does not exist.')


    @staticmethod
    def get_keys(user_name, client):
        """ Get the Access Key IDs of the user, and return them in a list.

        Returns:
            All access keys found for the IAM user, in a list.
            List will be empty if the user has no keys.
         """

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
        """ Generate temporary SSO access credentials.

        Requires the config file containing the IDP hostname.

        Returns:
            A temporary boto3 client created with a session token provided by the IDP host.

        Raises:
            A ValueError if the config path can not be found.
        """

        sso_config_path = '/etc/openshift_tools/sso-config.yaml'

        if os.path.isfile(sso_config_path):
            with open(sso_config_path, 'r') as sso_config:
                yaml_config = yaml.load(sso_config)

                if yaml_config["idp_host"]:
                    ops_idp_host = yaml_config["idp_host"]

                try:
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

                except ValueError as client_exception:
                    if 'Error retrieving SAML token' in client_exception.message and \
                    'Metadata not found' in client_exception.message:
                        print(client_exception)
                        print('Metadata for %s missing or misconfigured, skipping' % aws_account)

                    else:
                        raise

        else:
            raise ValueError(sso_config_path + 'does not exist.')

    @staticmethod
    def create_key(aws_account, user_name, client):
        """ Change an API key for the specified account.

        Returns:
            A response object from boto3, which contains information about the new IAM key.
            Their values can be accessed like:
            ['AccessKey']['AccessKeyId']
            ['AccessKey']['SecretAccessKey']
        """

        response = client.create_access_key(
            UserName=user_name
            )

        print('Key successfully created for:', aws_account)
        return response


    @staticmethod
    def delete_key(aws_account, user_name, key, client):
        """ Delete an API key for the specified account. """

        client.delete_access_key(
            UserName=user_name,
            AccessKeyId=key
            )

        print('Key successfully deleted for:', aws_account)
        return True


    @staticmethod
    def manage_timestamp(update=False):
        """ Update the expiration file, or create it if it does not already exist. """

        path = os.path.join(os.path.expanduser('~'), '.aws/credentials_expiration')
        exp_date = str(int(time.time())+180*24*60*60)

        if os.path.isfile(path) and update is True:
            print('File exists, overwriting.')
            with open(path, 'w') as open_file:
                open_file.write(exp_date)

        elif not os.path.isfile(path):
            print('File does not exist, creating.')
            with open(path, 'w') as open_file:
                open_file.write(exp_date)

        else:
            print('Checked for stamp file and it exists. No write was called, nothing to do here.')
            return True


    @staticmethod
    def write_credentials(aws_account, key_object):
        """ Write the profile for the user account to the AWS credentials file.

        Raise:
            A ValueError if the path to the credentials file does not exist.
        """

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
            raise ValueError(path + ' does not exist.')


    def run_all(self, args, ops_accounts):
        """ Loop through a list of every ops-managed AWS account and create API keys for each. """

        for aws_account in ops_accounts:
            matching = [s for s in ops_accounts if aws_account in s]
            account_name = matching[0].split(':')[0]
            account_number = matching[0].split(':')[1]
            client = self.get_token(account_number)

            if client:
                self.check_user(aws_account, args.user, client)
                current_accounts = self.get_all_profiles()
                existing_keys = self.get_keys(args.user, client)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)

                if aws_account not in current_accounts:
                    key_object = self.create_key(aws_account, args.user, client)
                    self.write_credentials(account_name, key_object)

        self.manage_timestamp(True)


    def run_one(self, args, ops_accounts):
        """ Create API keys for only the specified ops-managed AWS accounts. """

        for aws_account in args.profile:
            matching = [s for s in ops_accounts if aws_account in s]
            account_name = matching[0].split(':')[0]
            account_number = matching[0].split(':')[1]
            client = self.get_token(account_number)

            if client:
                self.check_user(aws_account, args.user, client)
                existing_keys = self.get_keys(args.user, client)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)
                        key_object = self.create_key(aws_account, args.user, client)
                        self.write_credentials(account_name, key_object)

                else:
                    key_object = self.create_key(aws_account, args.user, client)
                    self.write_credentials(account_name, key_object)

        self.manage_timestamp()


    def main(self):
        """ Main function. """

        args = self.check_arguments()
        ops_accounts = self.check_accounts()

        if args.profile and args.user:
            self.run_one(args, ops_accounts)

        elif args.all and args.user:
            self.run_all(args, ops_accounts)

        else:
            raise ValueError('No suitable arguments provided.')


if __name__ == '__main__':
    MANAGE = ManageKeys()
    MANAGE.main()
