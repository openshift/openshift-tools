#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script can be used to delete unwanted AWS IAM user accounts.
 It can be used on individual AWS accounts or for all ops accounts at once.

 Usage:

 For individual accounts:
 delete_iam_account -u <user-to-delete> -p ded-stage-aws -p ded-int-aws -p <some-other-account>


 For all accounts found in /etc/openshift_tools/aws_accounts.txt:
 delete_iam_account -u <user-to-delete> --all
"""

from __future__ import print_function

import argparse
import os
import sys
import yaml

# pylint: disable=import-error
import boto3
import botocore

from openshift_tools import saml_aws_creds


class DeleteUser(object):
    """ Class to delete an iam user from ops acounts. """


    def __init__(self):
        """ constructor """
        self.response = None


    @staticmethod
    def check_arguments():
        """ Ensure that an argument was passed in from the command line.

        Returns:
            Parsed argument(s), if provided
        """

        parser = argparse.ArgumentParser(description='Delete unwanted IAM accounts')
        parser.add_argument('-a', '--all',
                            help='Delete IAM user from every profile in ~/.aws/credentials',
                            action='store_true')
        parser.add_argument('-p', '--profile',
                            help='Delete IAM user from the specified profile',
                            action='append')
        parser.add_argument('-u', '--user',
                            help='Specify a username for the account')
        args = parser.parse_args()

        if not args.all and not args.profile:
            print('Specify an account ID or profile name.\n'
                  'To delete the user\'s IAM account from all AWS accounts on file, use \"--all\"\n'
                  'Usage:\n'
                  'example: {0} -u <user-to-delete> -p <account-name>\n'
                  'example: {0} -u <user-to-delete> --all'.format(parser.prog))
            sys.exit(10)
        if args.user != 'root':
            return args


    @staticmethod
    def get_ops_accounts():
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
            raise ValueError(path + 'does not exist')


    @staticmethod
    def delete_user(user_name, client):
        """ Delete an IAM user account. """

        client.remove_user_from_group(GroupName='admin', UserName=user_name)

        response = client.delete_user(
            UserName=user_name
            )

        return response


    def check_user(self, aws_account, user_name, client):
        """ Check if the user exists locally and in AWS. Deletes the IAM user if found. """

        try:
            client.get_user(UserName=user_name)
        except botocore.exceptions.ClientError as client_exception:
            if client_exception.response['Error']['Code'] == 'NoSuchEntity':
                print('IAM user does not exist in account:', aws_account)
                return True

        else:
            if user_name != 'root':
                try:
                    self.delete_login_profile(user_name, client)
                except botocore.exceptions.ClientError as client_exception:
                    if client_exception.response['Error']['Code'] == 'NoSuchEntity':
                        print('IAM user does not have a password for account:', aws_account)

                print("Found existing IAM account in %s\n"
                      "deleting IAM account for user %s" % (aws_account, user_name))
                response = self.delete_user(user_name, client)

                return response
            else:
                print('Unable to delete this user. Only ops users can be deleted with this tool.')


    @staticmethod
    def get_keys(user_name, client, aws_account):
        """ Get the Access Key IDs of the user, and return them in a list.

        Returns:
            All access keys found for the IAM user, in a list.
            List will be empty if the user has no keys.
         """

        try:
            client.list_access_keys(
                UserName=user_name)
        except botocore.exceptions.ClientError as client_exception:
            if client_exception.response['Error']['Code'] == 'NoSuchEntity':
                print('IAM user does not have any keys for account:', aws_account)
                keys_list = []
                return keys_list

        else:
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
        """ Delete an API key for the specified account. """

        response = client.delete_access_key(
            UserName=user_name,
            AccessKeyId=key
            )

        print('Found and deleted api key for:', aws_account)
        return response


    @staticmethod
    def delete_login_profile(user_name, client):
        """ Delete the login profile from the IAM account. """

        response = client.delete_login_profile(
            UserName=user_name
            )

        return response


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
            raise ValueError(sso_config_path + 'does not exist.')


    def main(self):
        """ Main function. """
        args = self.check_arguments()
        ops_accounts = self.get_ops_accounts()

        if args.profile and args.user:

            for aws_account in args.profile:
                matching = [s for s in ops_accounts if aws_account in s]
                account_number = matching[0].split(':')[1]
                client = self.get_token(account_number)
                existing_keys = self.get_keys(args.user, client, aws_account)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)

                self.check_user(aws_account, args.user, client)

        elif args.all and args.user:

            for aws_account in ops_accounts:
                matching = [s for s in ops_accounts if aws_account in s]
                account_number = matching[0].split(':')[1]
                client = self.get_token(account_number)

                existing_keys = self.get_keys(args.user, client, aws_account)

                if existing_keys:
                    for key in existing_keys:
                        self.delete_key(aws_account, args.user, key, client)

                self.check_user(aws_account, args.user, client)

        else:
            raise ValueError('No suitable arguments provided.')


if __name__ == '__main__':
    DELETE = DeleteUser()
    DELETE.main()
