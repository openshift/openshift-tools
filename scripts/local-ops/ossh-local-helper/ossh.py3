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
if args.verbose:
    logger.setLevel(logging.DEBUG)

if not args.bastion_user:
    args.bastion_user = ''
else:
    args.bastion_user = args.bastion_user + '@'

if not args.target_user:
    args.target_user = ''
else:
    args.target_user = args.target_user + '@'

def addQuotes(string):
    return '"' + string + '"'

def addSlashes(string):
    string = string.replace('*', '\\*')
    string = string.replace('$', '\\$')
    string = string.replace('"', '\\"')
    string = string.replace('\'', '\\\'')
    return string

def buildCmd(bastion, target, docker):

    ProxyCommand = 'ssh -q -W %h:%p ' + bastion["user"] + bastion["host"]

    if len(docker["cmd"]) > 0:
        docker["cmd"] = " ".join(docker["cmd"])
        docker["cmd"] = [addSlashes(docker["cmd"])]

    return [
        'ssh',
        '-o ProxyCommand="' + ProxyCommand + '"',
        '-o StrictHostKeyChecking=no',
    ] + target['ssh_opts'] + [
        target["user"] + target["host"],
    ] + target["cmd"] + docker["cmd"]

if __name__ == "__main__":
    bastion = {
        'host': args.bastion_host,
        'user': args.bastion_user,
    }
    target = {
        'host': args.target_host,
        'user': args.target_user,
        'ssh_opts': [
            #'-t',
        ],
        'cmd': [],
    }
    docker = {
        'cmd': [],
    }

    if len(args.arguments) > 0:
        if "mon" in args.arguments[0]:
            # add tty terminal
            target["ssh_opts"].append('-t')

            # force target bash
            target["cmd"] = ['/bin/bash -c']

            docker["cmd"] = [
                'echo %s' % args.target_host,
                '&&',
                'docker exec -it oso-rhel7-host-monitoring' ,
            ]

            dockerCmd = '/usr/bin/env /bin/bash'
            if args.arguments[1:]:
                dockerCmd = '/usr/bin/env /bin/bash -c ' + addQuotes(" ".join(args.arguments[1:]))
            docker["cmd"].append(dockerCmd)

        else:
            target["cmd"] = ['/bin/bash -c'] + args.arguments

    logger.debug(" ".join(buildCmd(bastion, target, docker)))
    subprocess.call(shlex.split(" ".join(buildCmd(bastion, target, docker))))
