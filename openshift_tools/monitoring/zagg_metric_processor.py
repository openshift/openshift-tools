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

"""zagg_metric_processor Module
The purpose of this module is to process metrics and send them to Zagg.
"""

# Reason: disable pylint too-few-public-methods because this class is a simple
#     helper / wrapper class.
# Status: permanently disabled
# pylint: disable=too-few-public-methods
class ZaggMetricProcessor(object):
    """Processes metrics and sends them to a zagg
    """

    def __init__(self, metric_manager, zagg_client):
        """Constructs the object

        Args:
            metric_manager: this is where we get the metrics from.
            zagg_client: this is where they're going to
        """
        self.metric_manager = metric_manager
        self.zagg_client = zagg_client

    def process_metrics(self):
        """Processes all metrics provided by metric_manager"""
        # Read metrics from disk
        metrics = self.metric_manager.read_metrics()

        if not metrics:
            print "nothing to do!"
            return True # we successfully sent 0 metrics to zagg

        status, _ = self.zagg_client.add_metric(metrics)

        if status == 200:
            # We've successfuly sent the metrics, so remove them from disk
            self.metric_manager.remove_metrics(metrics)
        else:
            # TODO: add logging of the failure, and signal of failure
            # For now, we'll just leave them on disk and try again
            pass
