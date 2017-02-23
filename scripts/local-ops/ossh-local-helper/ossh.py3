#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OSSH helper')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        #default=None,
        help='Verbose?',
    )

    parser.add_argument(
        '--bastion-host',
        required=True,
        type=str,
        help='bastion host proxy through',
    )

    parser.add_argument(
        '--bastion-user',
        type=str,
        help='user for bastion host',
    )

    parser.add_argument(
        '--target-host',
        required=True,
        type=str,
        help='target host',
    )

    parser.add_argument(
        '--target-user',
        type=str,
        help='user for target host',
    )

    parser.add_argument(
        'arguments',
        default=None,
        nargs=argparse.REMAINDER,
        help='additional arguments',
    )

    return parser.parse_args()

args = parse_args()

if not args.bastion_user:
    args.bastion_user = ''
else:
    args.bastion_user = args.bastion_user + '@'

if not args.target_user:
    args.target_user = ''
else:
    args.target_user = args.target_user + '@'

sshcmd = [
    'ssh ',
    '-o ProxyCommand="ssh -q -W %h:%p ' + args.bastion_user + args.bastion_host + '"',
    '-o StrictHostKeyChecking=no',
    args.target_user + args.target_host,
]

def show_verbose():
    #if args.verbose:
    if '-v'in args.arguments or args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("args:" + repr(args))
        logger.debug(" ".join(shlex.split(" ".join(sshcmd))))

def run_cmd(cmd):
    subprocess.call(cmd)

def main():
    show_verbose()
    if len(args.arguments) > 0:
        if "mon" in args.arguments[0]:
            sshcmd.insert(1, '-t')
            sshcmd.append('/usr/bin/bash -c "echo \"%s\"; docker exec -it oso-rhel7-host-monitoring bash"' % args.target_host)
            subprocess.call(shlex.split(" ".join(sshcmd)))
        else:
            sshcmd.append(args.arguments[0])
            subprocess.call(shlex.split(" ".join(sshcmd)))
    if len(args.arguments) == 0:
        subprocess.call(shlex.split(" ".join(sshcmd)))

if __name__ == "__main__":
    main()
