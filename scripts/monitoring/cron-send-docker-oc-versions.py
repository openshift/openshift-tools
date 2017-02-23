#!/usr/bin/python
'''
  Send openshift and docker versions with miq_metric tag to metric_sender

  Example:
  ./cron-send-docker-oc-versions.py
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name,import-error

import json
import os
import sys
import subprocess
import argparse
from openshift_tools.monitoring.metric_sender import MetricSender


def parse_args():
    '''Parse the arguments for this script'''
    parser = argparse.ArgumentParser(description="Tool to send docker and openshift versions")
    parser.add_argument('-d', '--debug', default=False, action="store_true", help="debug mode")
    parser.add_argument('-v', '--verbose', default=False, action="store_true", help="Verbose?")

    args = parser.parse_args()
    return args


def add_specific_rpm_version(package_name, rpm_db_path, keys, mts, key_prefix=""):
    '''get rpm package version and add to metric sender and keys dictionary
    '''
    try:
        return_value = subprocess.check_output("rpm --dbpath {rpm_db_path} -q {package}".format(rpm_db_path=rpm_db_path,
                                                                                                package=package_name),
                                               stderr=subprocess.STDOUT, shell=True)

        if return_value.startswith(package_name):
            package_version = return_value[len(package_name)+1:len(return_value)-1]
            key = "{prefix}{name}.version".format(prefix=key_prefix, name=package_name)
            tags = {"descriptor_name": "{name}.version".format(name=package_name),
                    "miq_metric": "true"}
            mts.add_metric({key: package_version}, key_tags=tags)
            keys[key] = package_version
            return True, None

    except subprocess.CalledProcessError as err:
        return False, err

def main():
    '''get docker and openshift versions and send to metric sender
    '''

    args = parse_args()
    mts = MetricSender(verbose=args.verbose, debug=args.debug)

    # Check if host rpm db is mounted. Otherwise check againts container db
    rpm_db_path = "/host/var/lib/rpm"
    if not os.path.exists(rpm_db_path):
        rpm_db_path = "/var/lib/rpm"

    keys = {}

    # Accumulate failures
    failures = 0

    # Get docker version
    success, err = add_specific_rpm_version("docker", rpm_db_path, keys, mts)
    if not success:
        failures += 1
        print "Failed to get docker rpm version. " + err.output


    openshift_package_name = "origin"

    # Get openshift node version (attempt upstream)
    success, err = add_specific_rpm_version("{}-node".format(openshift_package_name), rpm_db_path, keys, mts,
                                            "openshift.node.")
    if not success:
        # Get openshift version (attempt downstream)
        openshift_package_name = "atomic-openshift"
        success, err2 = add_specific_rpm_version("{}-node".format(openshift_package_name), rpm_db_path, keys, mts,
                                                 "openshift.node.")
        if not success:
            failures += 1
            print "Failed to get openshift rpm version:\n" + err.output + + err2.output

    # Get openshift master version (upstream or downstream) - only if node rpm found
    if success:
        success, err = add_specific_rpm_version("{}-master".format(openshift_package_name), rpm_db_path, keys, mts,
                                                "openshift.master.")
        if not success:
            # Print notification but don't count this as failure
            print "Note: " + err.output

    print "Sending these metrics:"
    print json.dumps(keys, indent=4)
    mts.send_metrics()
    print "\nDone.\n"

    sys.exit(failures)

if __name__ == '__main__':
    main()
