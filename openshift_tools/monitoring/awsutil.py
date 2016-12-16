#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Interface to awscli
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

import json
import os
import shlex
import subprocess

class AWSUtil(object):
    ''' Routines for interacting with awscli '''
    def __init__(self, access_key=None, secret_access_key=None, verbose=False):
        ''' Save auth details for later usage '''

        if access_key == None:
            self.access_key = os.environ["AWS_ACCESS_KEY_ID"]
        else:
            self.access_key = access_key

        if secret_access_key == None:
            self.secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        else:
            self.secret_access_key = secret_access_key

        self.verbose = verbose

    def _run_cmd(self, cmd):
        ''' Actually call out aws tool '''

        cmd = shlex.split(cmd)

        if self.verbose:
            print "Running command: " + str(cmd)
        results = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   env={'PATH': os.environ["PATH"],
                                        'AWS_ACCESS_KEY_ID': self.access_key,
                                        'AWS_SECRET_ACCESS_KEY': self.secret_access_key})
        results.wait()

        if results.returncode != 0:
            raise Exception("Non-zero return on command: {}".format(str(cmd)))

        return results.stdout.read()

    def get_bucket_list(self, verbose=False, BucketRegion=''):
        ''' Get list of all S3 buckets visible to AWS ID '''

        s3ls_cmd = "aws s3api list-buckets  "
        if not BucketRegion == '':
            s3ls_cmd = "aws s3api list-buckets --region " + BucketRegion

        buckets = self._run_cmd(s3ls_cmd)

        json_list = json.loads(buckets)

        bucket_list = []
        for bucket in json_list["Buckets"]:
            bucket_list.append(bucket["Name"])

        if verbose or self.verbose:
            print "Buckets found: " + str(bucket_list)

        return bucket_list

    def get_bucket_info(self, s3_bucket, verbose=False, BucketRegion=''):
        ''' Get size (in GB) and object count for S3 bucket '''
        aws_cmd = "aws s3 ls {}".format(s3_bucket)

        if not BucketRegion == '':
            aws_cmd = "aws s3 ls {}".format(s3_bucket)+" --region " + BucketRegion

        output = self._run_cmd(aws_cmd)

        # First check whether the bucket is completely empty
        # We can't do the s3api call futher below on an empty bucket
        if output == "":
            # Empty bucket, so just return size 0, object count 0
            return [0, 0]
        aws_cmd = ("aws s3api list-objects --bucket {}".format(s3_bucket)+" --query "
                   "\"[sum(Contents[].Size), length(Contents[])]\"")
        if not BucketRegion == '':
            aws_cmd = ("aws s3api list-objects --bucket {}".format(s3_bucket)+
                       " --output json --region " + BucketRegion + " --query "
                       "\"[sum(Contents[].Size), length(Contents[])]\"")

        s3_json = self._run_cmd(aws_cmd)

        s3_result = json.loads(s3_json)

        s3_size = s3_result[0]
        s3_objects = s3_result[1]

        if verbose or self.verbose:
            print "Bucket: {} Size: {} Objects: {}".format(s3_bucket, s3_size, s3_objects)

        s3_size_gb = float(s3_size) / 1024 / 1024 / 1024

        return [s3_size_gb, s3_objects]

