#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Collect and send gcs bucket stats
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
from openshift_tools.monitoring.gcputil import GcloudUtil
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
    volumes = yaml.safe_load(yaml_results)['spec']['template']['spec']['volumes']
    for volume in volumes:
        if 'emptyDir' in volume:
            continue
        secret_yaml = ocutil.get_secrets(volume['secret']['secretName'])
        secret_dict = yaml.safe_load(secret_yaml)
        if 'config.yml' in secret_dict['data']:
            return volume['secret']['secretName']

    print "Unable to find the %s the docker registry config"
    print "Please run \"oc get dc docker-registry\" to investigate"
    sys.exit(1)

def get_gcp_info(yaml_results):
    ''' Get bucket name for the docker-registry '''

    base64_text = yaml.safe_load(yaml_results)["data"]["config.yml"]

    base64_yaml = base64.b64decode(base64_text)

    gcp_details = yaml.safe_load(base64_yaml)

    bucket = gcp_details["storage"]["gcs"]["bucket"]

    return bucket

# pylint: disable=too-many-locals
def main():
    ''' Gather and send details on all visible S3 buckets '''

    discovery_key = "disc.gcp"
    discovery_macro = "#GCS_BUCKET"
    prototype_bucket_size = "disc.gcp.size"
    prototype_bucket_count = "disc.gcp.objects"

    args = parse_args()

    ocutil = OCUtil()
    dc_yaml = ocutil.get_dc('docker-registry')
    registry_config_secret = get_registry_config_secret(dc_yaml)

    oc_yaml = ocutil.get_secrets(registry_config_secret)

    bucket = get_gcp_info(oc_yaml)
    gsutil = GcloudUtil(verbose=args.debug)

    bucket_list = gsutil.get_bucket_list()

    bucket_stats = {}

    for bucket in bucket_list:
        size, objects = gsutil.get_bucket_info(bucket)
        bucket_stats[bucket] = {"size": size, "objects": objects}

    if args.debug:
        print "Bucket stats: " + str(bucket_stats)

    if args.test:
        print "Test-only. Received results: " + str(bucket_stats)
    else:
        zgs = ZaggSender(verbose=args.debug)
        zgs.add_zabbix_dynamic_item(discovery_key, discovery_macro, bucket_list)
        for bucket in bucket_stats.keys():
            zab_key = "{}[{}]".format(prototype_bucket_size, bucket)
            zgs.add_zabbix_keys({zab_key: int(round(bucket_stats[bucket]["size"]))})

            zab_key = "{}[{}]".format(prototype_bucket_count, bucket)
            zgs.add_zabbix_keys({zab_key: bucket_stats[bucket]["objects"]})
        zgs.send_metrics()

if __name__ == '__main__':
    main()

