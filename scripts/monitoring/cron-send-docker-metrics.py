#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker info data gatherer
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


from docker import AutoVersionClient
from docker.errors import DockerException
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.timeout import TimeoutException
from openshift_tools.monitoring.dockerutil import DockerUtil
import json

if __name__ == "__main__":
    keys = None
    zs = ZaggSender()
    try:
        cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
        du = DockerUtil(cli)
        du_dds = du.get_disk_usage()

        keys = {
            'docker.storage.data.space.used': du_dds.data_space_used,
            'docker.storage.data.space.available': du_dds.data_space_available,
            'docker.storage.data.space.percent_available': du_dds.data_space_percent_available,
            'docker.storage.data.space.total': du_dds.data_space_total,

            'docker.storage.metadata.space.used': du_dds.metadata_space_used,
            'docker.storage.metadata.space.available': du_dds.metadata_space_available,
            'docker.storage.metadata.space.percent_available': du_dds.metadata_space_percent_available,
            'docker.storage.metadata.space.total': du_dds.metadata_space_total,

            'docker.storage.is_loopback': int(du_dds.is_loopback),
            'docker.ping': 1, # Docker is up
        }
    except (DockerException, TimeoutException) as ex:
        print "\nERROR talking to docker: %s\n" % ex.message
        keys = {
            'docker.ping': 0,  # Docker is down
        }

    zs.add_zabbix_keys(keys)

    print "Sending these metrics:"
    print json.dumps(keys, indent=4)
    zs.send_metrics()
    print "\nDone.\n"
