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

"""zabbix_metric_processor Module
The purpose of this module is to process metrics and send them to Zabbix.
"""

from openshift_tools.monitoring.metricmanager import UniqueMetric
from zbxsend import send_to_zabbix

# Reason: disable pylint too-few-public-methods because this class is a simple
#     helper / wrapper class.
# Status: permanently disabled
# pylint: disable=too-few-public-methods
class ZabbixSender(object):
    """Used as a wrapper to bind together the authentication and the send call.
    """
    def __init__(self, server, port):
        """Constructs the object

        Args:
            server: the zabbix server where the trapper is running
            port: the zabbix port that the trapper is listening on
        """
        self.server = server
        self.port = port

    def send(self, metrics):
        """Sends the metric information to the zabbix trapper.

        Args:
            metrics: a list of UniqueMetrics to send to zabbix.

        Returns: a boolean
            True: metrics were successfully sent to zabbix.
            False: an error occurred.
        """
        return send_to_zabbix(metrics, self.server, self.port)

class ZabbixMetricProcessor(object):
    """Processes metrics and sends them to Zabbix Trapper.
    """

    def __init__(self, metric_manager, zbxapi, zbxsender):
        """Constructs the object

        Args:
            metric_manager: this is where we get the metrics from.
            zbxapi: this is used for heartbeat metrics
            zbxsender: this is used to send the metrics to zabbix
        """
        self.metric_manager = metric_manager
        self.zbxapi = zbxapi
        self.zbxsender = zbxsender

    def process_metrics(self):
        """Processes all metrics provided by metric_manager"""
        # Read metrics from disk
        all_metrics = self.metric_manager.read_metrics()

        # Process heartbeat metrics First (this ordering is important)
        # This ensures a host in zabbix has been created.
        self._process_heartbeat_metrics(self.metric_manager.filter_heartbeat_metrics(all_metrics))

        # Now process normal metrics
        self._process_normal_metrics(self.metric_manager.filter_zbx_metrics(all_metrics))

    def _process_heartbeat_metrics(self, hb_metrics):
        """Processes heartbeat metrics.

        This ensures that there is a host entry in zabbix, then
        sends a value for the heartbeat item.

        Args:
            hb_metrics: a list of heartbeat metrics to process.

        Returns: nothing
        """
        for hb_metric in hb_metrics:
            templates = hb_metric.value['templates']
            hostgroups = hb_metric.value['hostgroups']

            # Make sure there is a host entry in zabbix
            host_res = self.zbxapi.ensure_host_is_present(
                hb_metric.host,
                templates,
                hostgroups)

            # Actually do the heartbeat now
            hbum = UniqueMetric(hb_metric.host, 'heartbeat.ping', 1)
            hb_res = self.zbxsender.send([hbum])

            # Remove the metric if we were able to successfully heartbeat
            if host_res and hb_res:
                # We've successfuly sent the heartbeat, so remove it from disk
                self.metric_manager.remove_metrics(hb_metric)
            else:
                # TODO: add logging of the failure, and signal of failure
                # For now, we'll just leave them on disk and try again
                pass

    def _process_normal_metrics(self, metrics):
        """Processes normal metrics.

        This sends the metric data to the zabbix trapper.
        sends a value for the heartbeat item.

        Args:
            metrics: a list of metrics to send to zabbix.

        Returns: nothing
        """
        if not metrics:
            return True # we successfully sent 0 metrics to zabbix

        if self.zbxsender.send(metrics):
            # We've successfuly sent the metrics, so remove them from disk
            self.metric_manager.remove_metrics(metrics)
        else:
            # TODO: add logging of the failure, and signal of failure
            # For now, we'll just leave them on disk and try again
            pass
