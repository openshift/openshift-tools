#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
''' Script to take trigger data from zabbix and forward to bastion host '''

#
#   Copyright 2015 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

import argparse
import subprocess
import yaml

CONF_FILE = "/etc/zabbix/ops_zbx_event_processor.yml"
BASTION_HEAL_CMD = "opsmedic-healer"

def process_event():
    ''' main function to do processing '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--trigger")
    parser.add_argument("--trigger-val")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    conf_f = open(CONF_FILE)
    conf_yml = yaml.safe_load(conf_f)
    conf_f.close()

    rsa_key = conf_yml['rsa_key']
    scriptrunner_user = conf_yml['scriptrunner_user']
    bastion_host = conf_yml['bastion_host']

    cmd = ["ssh", "-i", rsa_key, "-l", scriptrunner_user, bastion_host,
           BASTION_HEAL_CMD + " --host \\\"" + args.host + "\\\" --trigger \\\"" + \
           args.trigger + "\\\" --trigger-val \\\"" + args.trigger_val + "\\\""]

    if args.verbose:
        print "Running: " + ' '.join(cmd)

    result = subprocess.call(cmd)

    print "remote command returned: " + str(result)

if __name__ == "__main__":
    process_event()
