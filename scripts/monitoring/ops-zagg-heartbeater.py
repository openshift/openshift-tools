#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

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

"""This is a script that adds a heartbeat to all defined targets in zagg.
"""

from openshift_tools.monitoring.metricmanager import MetricManager, UniqueMetric
import yaml
import socket

# Reason: This class has the API we want.
# Status: permanently disabled
# pylint: disable=too-few-public-methods
class ZaggHeartbeater(object):
    """Adds heartbeats for all targets found in /etc/openshift_tools/zagg_server.yaml
    """

    def __init__(self, config_file):
        """Constructs the object

        Args:
            config_file: path to the config file on disk
        """

        self.config = yaml.load(file(config_file))

    def run(self):
        """Runs through each defined target in the config file and sends a heartbeat

        Args: None
        Returns: None
        """
        for target in self.config['targets']:
            mm = MetricManager(target['path'])

            hostname = socket.gethostname()
            myhb = UniqueMetric.create_heartbeat(hostname, self.config['templates'], self.config['hostgroups'])

            print 'Writing heartbeat to %s/%s' % (target['path'], myhb.filename)
            mm.write_metrics(myhb)

if __name__ == "__main__":
    # Currently only supports writing the heartbeat locally, but might be
    # changed to send it remotely to a zagg web.
    ZaggHeartbeater('/etc/openshift_tools/zagg_server.yaml').run()
