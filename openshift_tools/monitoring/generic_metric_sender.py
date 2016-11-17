#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Base class for sending metrics
"""

import os
import yaml


class GenericMetricSenderException(Exception):
    '''
        GenericMetricSenderException
        Exists to propagate errors up from the api
    '''
    pass

class GenericMetricSender(object):
    """
    Abstract class that encapsulates all metric sending operations.
    """

    # pylint: disable=unidiomatic-typecheck
    def __init__(self):
        """ raise exception - Abstract class shouldn't instantiate"""
        if type(self) is GenericMetricSender:
            raise TypeError("This is an abstract class and shouldn't be directly instantiated")

        self.unique_metrics = []
        self.config = None
        self.config_file = None


    def parse_config(self):
        """ parse default config file """
        if not self.config:
            if not os.path.exists(self.config_file):
                raise GenericMetricSenderException(self.config_file + " does not exist.")
            self.config = yaml.load(file(self.config_file))

    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def add_dynamic_metric(self, discovery_key, macro_string, macro_array, host=None, synthetic=False):
        """ empty implementation overridden by derived classes """
        pass

    def add_metric(self, metric, host=None, synthetic=False):
        """ empty implementation overridden by derived classes """
        pass

    def add_heartbeat(self, add_heartbeat, host=None):
        """ empty implementation overridden by derived classes """
        pass

    def send_metrics(self):
        """ empty implementation overridden by derived classes """
        pass

    def print_unique_metrics_key_value(self):
        """
        This function prints the key/value pairs the UniqueMetrics that sender
        currently has stored
        """
        print "\n" + self.__class__.__name__ + " Key/Value pairs:"
        print "=============================="
        for unique_metric in self.unique_metrics:
            print("%s:  %s") % (unique_metric.key, unique_metric.value)
        print "==============================\n"

    def print_unique_metrics(self):
        """
        This function prints all of the information of the UniqueMetrics that sender
        currently has stored
        """
        print "\n" + self.__class__.__name__ + " UniqueMetrics:"
        print "=============================="
        for unique_metric in self.unique_metrics:
            print unique_metric
        print "==============================\n"

