#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This script can be used to reset the passwords for your AWS IAM user accounts.
 It can be used for an individual account or for all your accounts at once.

 This assumes that the AWS credentials for the account(s) are present in "~/.aws/credentials"
 The credentials entry must also be labeled with a name:

 [account-name-or-number]
 aws_access_key_id=xxxx
 aws_secret_access_key=xxxx

 Usage:

  for an individual account:
 change_iam_password.py -p ded-stage-aws
 or
 change_iam_password.py -p 123456789012

 For all accounts found in ~/.aws/credentials:
 change_iam_password.py --all
"""

from __future__ import print_function

import argparse
import getpass
import os
import re
import sys

import boto3


def check_arguments():
    """ ensure that an argument was passed in from the command line """

    parser = argparse.ArgumentParser(description='Change the password for one or all IAM accounts')
    parser.add_argument("-a", "--all",
                        help="change the password for every profile in ~/.aws/credentials",
                        action="store_true")
    parser.add_argument("-p", "--profile",
                        help="change the password for the specified profile")
    parser.parse_args()

    if len(sys.argv) < 2:
        print ('Specify an account ID or profile name. \
        To change the password for all accounts on file, use \"--all\"')
        print('Usage:')
        print('example: %s <account-id-number>' % sys.argv[0])
        print('example: %s --all' % sys.argv[0])
        sys.exit(10)
    else:
        return True


def get_all_profiles():
    """ if -a is specified, generate a list of all profiles found in ~/.aws/credentials """

    path = os.path.expanduser('~') + '/.aws/credentials'
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
        raise ValueError(path + 'does not exist')


def change_password(aws_account, old_password, new_password):
    """ change the password for the specified account"""

    session = boto3.Session(profile_name=aws_account)
    client = session.client('iam')

    response = client.change_password(
        OldPassword=old_password,
        NewPassword=new_password
        )

    print('Password successfully changed for:', aws_account)
    return response


def main():
    """ main function """

    check_arguments()

    current_password = getpass.getpass('Old Password:')
    new_password = getpass.getpass('New Password:')
    confirm_password = getpass.getpass('Confirm New Password:')

    if new_password != confirm_password:
        raise ValueError('New password does not match confirmation')

    else:
        if sys.argv[1] == '-p' and sys.argv[2] or sys.argv[1] == '--profile' and sys.argv[2]:
            aws_account = sys.argv[2]
            change_password(aws_account, current_password, confirm_password)

        elif sys.argv[1] == '-a' or sys.argv[1] == '--all':
            for aws_account in get_all_profiles():
                change_password(aws_account, current_password, confirm_password)

        else:
            raise ValueError('No suitable arguments provided')

if __name__ == '__main__':
    main()
