#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    Quick and dirty docker info data gatherer
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


from docker import AutoVersionClient
from docker.errors import DockerException
from openshift_tools.monitoring.zagg_sender import ZaggSender
import json
import re
import sys

class DockerDiskStats(object):
    ''' Class to store docker storage information
    '''

    # Reason: disable pylint too-many-instance-attributes and too-few-public-methods
    #         because this is a DTO
    # Status: permanently disabled
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self):
        ''' construct the object
        '''
        self.data_space_used = None
        self.data_space_available = None
        self.data_space_total = None
        self.data_space_percent_available = None

        self.metadata_space_used = None
        self.metadata_space_available = None
        self.metadata_space_total = None
        self.metadata_space_percent_available = None
        self.is_loopback = None

    def __repr__(self):
        ''' make it easy to see what's inside of this object
        '''
        return 'DockerDiskStats(\n' + \
               '  is loopback: %r\n' % self.is_loopback + \
               '  data_space_used: %r\n' % self.data_space_used + \
               '  data_space_available: %r\n' % self.data_space_available + \
               '  data_space_total: %r\n' % self.data_space_total + \
               '  data_space_percent_available: %r\n' % self.data_space_percent_available + \
               '  metadtata_space_used: %r\n' % self.metadata_space_used + \
               '  metadtata_space_available: %r\n' % self.metadata_space_available + \
               '  metadtata_space_total: %r\n' % self.metadata_space_total + \
               '  metadata_space_percent_available: %r\n' % self.metadata_space_percent_available + \
               ')'

class ParseError(Exception):
    ''' Exception class for when we can't parse the docker info
    '''
    pass

# FIXME: Break these out into classes, and put them in their own rpm
class DockerWatcher(object):
    ''' Class grab docker storage information
    '''
    def __init__(self, docker_client=None):
        ''' construct the object
        '''
        self.docker = docker_client
        self.docker_info = self.docker.info()
        #print json.dumps(self.docker_info, indent=4)

    @staticmethod
    def convert_to_size_in_gb(value):
        ''' Parses out the number and unit type and normalizes the data to GB
        '''
        matches = re.match(r"^(?P<num>[0-9.]+) (?P<unit>[a-zA-Z]+)", value)
        num = matches.group("num")
        unit = matches.group("unit")

        if unit == "GB":
            return float(num)

        if unit == "MB":
            return float(num) / 1024

        if unit == "kB":
            return float(num) / (1024 * 1024)

        raise ParseError("Unknown Unit Size")

    def get_driver_status_attr(self, key):
        ''' Gets the value for the specified key from the DriverStatus hash since it's
            an array of key/value pairs instead of a normal dict (PITA to work with otherwise)
        '''
        return [a[1] for a in self.docker_info['DriverStatus'] if a[0] == key][0]

    def get_disk_usage(self):
        ''' Gathers the docker storage disk usage stats and puts them in a DTO.
        '''
        dds = DockerDiskStats()
        dds.data_space_used = DockerWatcher.convert_to_size_in_gb( \
                                self.get_driver_status_attr('Data Space Used'))

        dds.data_space_available = DockerWatcher.convert_to_size_in_gb( \
                                self.get_driver_status_attr('Data Space Available'))

        dds.data_space_total = DockerWatcher.convert_to_size_in_gb( \
                                self.get_driver_status_attr('Data Space Total'))

        dds.metadata_space_used = DockerWatcher.convert_to_size_in_gb( \
                                self.get_driver_status_attr('Metadata Space Used'))

        dds.metadata_space_available = DockerWatcher.convert_to_size_in_gb( \
                                self.get_driver_status_attr('Metadata Space Available'))

        dds.metadata_space_total = DockerWatcher.convert_to_size_in_gb( \
                                self.get_driver_status_attr('Metadata Space Total'))


        # Determine if docker is using a loopback device
        # FIXME: find a better way than allowing this to throw
        try:
            self.get_driver_status_attr('Data loop file')
            dds.is_loopback = True
        except IndexError:
            dds.is_loopback = False

        # Work around because loopback lies about it's actual total space
        if not dds.is_loopback:
            dds.data_space_total = dds.data_space_used + dds.data_space_available
            dds.metadata_space_total = dds.metadata_space_used + dds.metadata_space_available


        dds.data_space_percent_available = (dds.data_space_available / dds.data_space_total) * 100
        dds.metadata_space_percent_available = (dds.metadata_space_available / dds.metadata_space_total) * 100

        return dds

if __name__ == "__main__":
    keys = None
    exit_code = 0
    zs = ZaggSender()
    try:
        cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
        dw = DockerWatcher(cli)
        dw_dds = dw.get_disk_usage()

        keys = {
            'docker.storage.data.space.used': dw_dds.data_space_used,
            'docker.storage.data.space.available': dw_dds.data_space_available,
            'docker.storage.data.space.percent_available': dw_dds.data_space_percent_available,
            'docker.storage.data.space.total': dw_dds.data_space_total,

            'docker.storage.metadata.space.used': dw_dds.metadata_space_used,
            'docker.storage.metadata.space.available': dw_dds.metadata_space_available,
            'docker.storage.metadata.space.percent_available': dw_dds.metadata_space_percent_available,
            'docker.storage.metadata.space.total': dw_dds.metadata_space_total,

            'docker.storage.is_loopback': int(dw_dds.is_loopback),
            'docker.ping': 1, # Docker is up
        }
    except DockerException as ex:
        print "\nERROR talking to docker: %s\n" % ex.message
        keys = {
            'docker.ping': 0,  # Docker is down
        }
        exit_code = 10

    zs.add_zabbix_keys(keys)

    print "Sending these metrics:"
    print json.dumps(keys, indent=4)
    zs.send_metrics()
    print "\nDone.\n"
    sys.exit(exit_code)
