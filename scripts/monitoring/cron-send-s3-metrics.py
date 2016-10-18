#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Collect and send AWS S3 bucket stats
'''
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
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name
# pylint: disable=import-error

import argparse
import base64
from openshift_tools.monitoring.awsutil import AWSUtil
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.zagg_sender import ZaggSender
import sys
import yaml

def parse_args():
    '''Parse the arguments for this script'''

    parser = argparse.ArgumentParser(description="Tool to get S3 bucket stats")
    parser.add_argument('-d', '--debug', default=False,
                        action="store_true", help="debug mode")
    parser.add_argument('-t', '--test', default=False,
                        action="store_true", help="Run the script but don't send to zabbix")
    args = parser.parse_args()
    return args

def get_registry_config_secret(yaml_results):
    ''' Find the docker registry config secret '''

    ocutil = OCUtil()
    volumes = yaml_results['spec']['template']['spec']['volumes']
    for volume in volumes:
        if 'emptyDir' in volume:
            continue
        secret_dict = ocutil.get_secrets(volume['secret']['secretName'])
        if 'config.yml' in secret_dict['data']:
            return volume['secret']['secretName']

    print "Unable to find the %s the docker registry config"
    print "Please run \"oc get dc docker-registry\" to investigate"
    sys.exit(1)

def get_aws_creds(yaml_results):
    ''' Get AWS authentication and S3 bucket name for the docker-registry '''

    base64_text = yaml_results["data"]["config.yml"]

    base64_yaml = base64.b64decode(base64_text)

    aws_details = yaml.safe_load(base64_yaml)
    aws_access_key = aws_details["storage"]["s3"]["accesskey"]
    aws_secret_key = aws_details["storage"]["s3"]["secretkey"]

    return [aws_access_key, aws_secret_key]

def main():
    ''' Gather and send details on all visible S3 buckets '''

    discovery_key = "disc.aws"
    discovery_macro = "#S3_BUCKET"
    prototype_s3_size = "disc.aws.size"
    prototype_s3_count = "disc.aws.objects"

    args = parse_args()

    ocutil = OCUtil()
    dc_yaml = ocutil.get_dc('docker-registry')
    registry_config_secret = get_registry_config_secret(dc_yaml)

    oc_yaml = ocutil.get_secrets(registry_config_secret)

    aws_access, aws_secret = get_aws_creds(oc_yaml)
    awsutil = AWSUtil(aws_access, aws_secret, args.debug)

    bucket_list = awsutil.get_bucket_list(args.debug)

    bucket_stats = {}

    for bucket in bucket_list:
        s3_size, s3_objects = awsutil.get_bucket_info(bucket, args.debug)
        bucket_stats[bucket] = {"size": s3_size, "objects": s3_objects}

    if args.debug:
        print "Bucket stats: " + str(bucket_stats)

    if args.test:
        print "Test-only. Received results: " + str(bucket_stats)
    else:
        zgs = ZaggSender(verbose=args.debug)
        zgs.add_zabbix_dynamic_item(discovery_key, discovery_macro, bucket_list)
        for bucket in bucket_stats.keys():
            zab_key = "{}[{}]".format(prototype_s3_size, bucket)
            zgs.add_zabbix_keys({zab_key: int(round(bucket_stats[bucket]["size"]))})

            zab_key = "{}[{}]".format(prototype_s3_count, bucket)
            zgs.add_zabbix_keys({zab_key: bucket_stats[bucket]["objects"]})
        zgs.send_metrics()

if __name__ == '__main__':
    main()
