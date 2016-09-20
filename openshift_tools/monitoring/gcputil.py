#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Interface to gcloud
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
import shlex
import subprocess
# Used for the low level google-api-python-client
# pylint: disable=import-error,unused-import
from apiclient.discovery import build
from oauth2client.client import GoogleCredentials

class GcloudUtil(object):
    ''' Routines for interacting with gcloud'''
    def __init__(self, gcp_creds_path='/root/.gce/creds.json', verbose=False):
        ''' Save auth details for later usage '''

        if not gcp_creds_path:
            credentials = GoogleCredentials.get_application_default()
        else:
            credentials = GoogleCredentials.from_stream(gcp_creds_path)

        self._credentials = credentials
        self.creds_path = gcp_creds_path
        self.verbose = verbose

        self.auth_activate_svc_account()

    def _run_cmd(self, cmd, out_format=None):
        ''' Actually call out aws tool '''

        cmd = shlex.split(cmd)

        if self.verbose:
            print "Running command: " + str(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        rval = stdout

        if proc.returncode != 0:
            raise Exception("Non-zero return on command: {}. Error: [{}]".format(str(cmd), stderr))

        if out_format == 'json':
            try:
                rval = json.loads(rval)
            except ValueError as _:
                # Error parsing output
                pass

        return rval

    def auth_activate_svc_account(self):
        '''activate a svc account'''
        cmd = 'gcloud auth activate-service-account --key-file %s' % self.creds_path
        self._run_cmd(cmd)

    def get_bucket_list(self):
        ''' Get list of all S3 buckets visible to AWS ID '''

        gcs_cmd = "gsutil ls gs://"
        buckets = self._run_cmd(gcs_cmd)

        # strip the gs:// and trailing / on each bucket
        buckets = [bucket[5:-1] for bucket in buckets.strip().split('\n')]

        if self.verbose:
            print "Buckets found: " + str(buckets)

        return buckets

    def get_bucket_info(self, bucket):
        ''' Get size (in GB) and object count for bucket
            Currently object is unsupported.
            gsutil does not have an easy way to return an object count that
              returns in a timely manner.
            gsutil ls -lR gs://bucket | tail -n 1
            gsutil du gs://bucket | wc -l
        '''

        cmd = "gsutil du -s gs://{}".format(bucket)
        output = self._run_cmd(cmd)
        if self.verbose:
            print "cmd: %s.  Results: [%s]" % (cmd, output)

        # First check whether the bucket is completely empty
        if output == "":
            # Empty bucket, so just return size 0, object count 0
            return [0, 0]

        size = int(output.split()[0])

        if self.verbose:
            print "Bucket: {} Size: {} Objects: {}".format(bucket, size, 0)

        size_gb = float(size) / 1024 / 1024 / 1024

        return [size_gb, 0]

