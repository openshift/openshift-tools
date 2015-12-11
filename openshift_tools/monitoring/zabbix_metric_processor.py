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

# This is the size of each chunk that we send to zabbix. We're defaulting to
# the size that the zabbix sender uses.
CHUNK_SIZE = 250

from openshift_tools.monitoring.metricmanager import UniqueMetric
# Reason: disable pylint import-error because it does not exist in the buildbot
# Status: permanently disabled
# pylint: disable=import-error
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

    # Reason: This is the API I want (stylistic exception)
    # Status: permanently disabled
    # pylint: disable=too-many-arguments
    def __init__(self, metric_manager, zbxapi, zbxsender, hostname, verbose=False):
        """Constructs the object

        Args:
            metric_manager: this is where we get the metrics from.
            zbxapi: this is used for heartbeat metrics
            zbxsender: this is used to send the metrics to zabbix
            hostname: the hostname of the zagg processor (so it can be overridden)
            verbose: whether this class should output or not.
        """
        self.metric_manager = metric_manager
        self.zbxapi = zbxapi
        self.zbxsender = zbxsender
        self._verbose = verbose
        self._hostname = hostname

    # TODO: change this over to use real logging.
    def _log(self, message):
        """Prints out the message if verbose is set.

        This is used as a helper so that we don't have to check the verbose flag every time.

        Args:
            message: the message to log.

        Returns: None
        """
        if self._verbose:
            print message

    def process_metrics(self):
        """Processes all metrics provided by metric_manager

        Args: None

        Returns: a list of errors, if any
        """

        # Read metrics from disk
        all_metrics = self.metric_manager.read_metrics()

        # Process heartbeat metrics First (this ordering is important)
        # This ensures a host in zabbix has been created.
        hb_metrics = self.metric_manager.filter_heartbeat_metrics(all_metrics)
        hb_errors = self._process_heartbeat_metrics(hb_metrics)

        # Now process normal metrics
        zbx_metrics = self.metric_manager.filter_zbx_metrics(all_metrics)
        metrics_errors = self._process_normal_metrics(zbx_metrics)

        # We need to know how many errors there were
        all_errors = hb_errors + metrics_errors

        # Now we need to try to send our zagg processor metrics.
        zagg_metrics = []
        zagg_metrics.append(UniqueMetric(self._hostname, 'zagg.server.heartbeat.count',
                                         len(hb_metrics)))
        zagg_metrics.append(UniqueMetric(self._hostname, 'zagg.server.metrics.count',
                                         len(zbx_metrics)))
        zagg_metrics.append(UniqueMetric(self._hostname, 'zagg.server.processor.errors',
                                         len(all_errors)))

        # We write them to disk so that we can retry sending this on error
        self.metric_manager.write_metrics(zagg_metrics)

        zagg_metrics_errors = self._process_normal_metrics(zagg_metrics)

        return all_errors + zagg_metrics_errors

    def _handle_templates(self, all_templates):
        """Handle templates by ensuring they exist.

        This ensures that the passed in templates exist in Zabbix.

        Args:
            all_templates: a list of templates to ensure exist.

        Returns: a list of errors, if any
        """

        errors = []
        try:
            # Make sure there is a template entry in zabbix
            for template in set(all_templates):
                self.zbxapi.ensure_template_exists(template)

        # Reason: disable pylint broad-except because we want to process as much as possible
        # Status: permanently disabled
        # pylint: disable=broad-except
        except Exception as error:
            self._log("Failed creating templates" % error.message)
            errors.append(error)

        return errors

    def _handle_hostgroups(self, all_hostgroups):
        """Handle hostgroups by ensuring they exist.

        This ensures that the passed in hostgroups exist in Zabbix.

        Args:
            all_hostgroups: a list of hostgroups to ensure exist.

        Returns: a list of errors, if any
        """

        errors = []
        try:
            # Make sure there is a hostgroup entry in zabbix
            for hostgroup in set(all_hostgroups):
                self.zbxapi.ensure_hostgroup_exists(hostgroup)

        # Reason: disable pylint broad-except because we want to process as much as possible
        # Status: permanently disabled
        # pylint: disable=broad-except
        except Exception as error:
            self._log("Failed creating hostgroups" % error.message)
            errors.append(error)

        return errors


    def _process_heartbeat_metrics(self, hb_metrics):
        """Processes heartbeat metrics.

        This ensures that there is a host entry in zabbix, then
        sends a value for the heartbeat item.

        Args:
            hb_metrics: a list of heartbeat metrics to process.

        Returns: a list of errors, if any
        """

        self._log("\nTotal Heartbeat Metrics to Send: %s\n" % len(hb_metrics))

        errors = []
        all_templates = []
        all_hostgroups = []

        # Collect all templates and hostgroups so we only process them 1 time.
        for hb_metric in hb_metrics:
            all_templates.extend(hb_metric.value['templates'])
            all_hostgroups.extend(hb_metric.value['hostgroups'])

        # Handle the Templates
        errors.extend(self._handle_templates(all_templates))

        # Handle the Hostgroups
        errors.extend(self._handle_hostgroups(all_hostgroups))

        for i, hb_metric in enumerate(hb_metrics):

            try:
                templates = hb_metric.value['templates']
                hostgroups = hb_metric.value['hostgroups']

                # Make sure there is a host entry in zabbix
                host_res = self.zbxapi.ensure_host_exists(hb_metric.host, templates, hostgroups)

                # Actually do the heartbeat now
                hbum = UniqueMetric(hb_metric.host, 'heartbeat.ping', 1)
                hb_res = self.zbxsender.send([hbum])

                # Remove the metric if we were able to successfully heartbeat
                if host_res and hb_res:
                    self._log("Sending heartbeat metric %s for host [%s] to Zabbix: success" % \
                                 (i + 1, hb_metric.host))

                    # We've successfuly sent the heartbeat, so remove it from disk
                    self.metric_manager.remove_metrics(hb_metric)
                else:
                    raise Exception("Error while sending to zabbix")

            # Reason: disable pylint broad-except because we want to process as much as possible
            # Status: permanently disabled
            # pylint: disable=broad-except
            except Exception as error:
                self._log("Sending heartbeat metric %s for host [%s] to Zabbix: FAILED: %s" % \
                             (i + 1, hb_metric.host, error.message))

                errors.append(error)

        return errors

    def _process_normal_metrics(self, metrics):
        """Processes normal metrics.

        This sends the metric data to the zabbix trapper.
        sends a value for the heartbeat item.

        Args:
            metrics: a list of metrics to send to zabbix.

        Returns: a list of errors, if any
        """

        self._log("\nTotal Normal Metrics to Send: %s" % len(metrics))
        self._log("                  Chunk Size: %s\n" % CHUNK_SIZE)

        if not metrics:
            return [] # we successfully sent 0 metrics to zabbix

        # Accumulate the errors
        errors = []

        # Send metrics to Zabbix in chunks
        for i, chunk_ix in enumerate(range(0, len(metrics), CHUNK_SIZE)):
            chunk = metrics[chunk_ix:(chunk_ix + CHUNK_SIZE)]

            try:
                if self.zbxsender.send(chunk):
                    self._log("Sending normal metrics chunk %s to Zabbix (size %s): success" % \
                                 (i + 1, len(chunk)))

                    # We've successfuly sent the metrics chunk, so remove them from disk
                    self.metric_manager.remove_metrics(chunk)
                else:
                    raise Exception("Error while sending to zabbix")

            # Reason: disable pylint broad-except because we want to process as much as possible
            # Status: permanently disabled
            # pylint: disable=broad-except
            except Exception as error:
                errors.append(error)
                self._log("Sending normal metrics chunk %s to Zabbix (size %s): FAILED: %s" % \
                             (i + 1, len(chunk), error.message))

        return errors
