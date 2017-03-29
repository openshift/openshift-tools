#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker info data gatherer
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name,import-error


from docker import AutoVersionClient
from docker.errors import DockerException
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.timeout import TimeoutException
from openshift_tools.monitoring.dockerutil import DockerUtil
import json
import psutil

def getRssVmsofDocker():
    """get rss and vms for docker"""
    docker_memoryusage = {}
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if pinfo['name'] == 'dockerd-current':
                #print pinfo
                docker_p = psutil.Process(pinfo['pid'])
                #print docker_p.memory_info().rss
                #print docker_p.memory_info().vms
                docker_memoryusage['rss'] = docker_p.memory_info().rss
                docker_memoryusage['vms'] = docker_p.memory_info().vms
        except psutil.NoSuchProcess:
            print 'error'

    return docker_memoryusage

if __name__ == "__main__":
    keys = None
    ms = MetricSender()

    try:
        cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
        du = DockerUtil(cli)
        du_dds = du.get_disk_usage()
        docker_memoryusages = getRssVmsofDocker()
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
        if docker_memoryusages.has_key('rss'):
            keys['docker.memoryusage.rss'] = int(docker_memoryusages['rss'])
            keys['docker.memoryusage.vms'] = int(docker_memoryusages['vms'])
        else:
            # this means this is a master , there is not dockerd
            pass

    except (DockerException, TimeoutException) as ex:
        print "\nERROR talking to docker: %s\n" % ex.message
        keys = {
            'docker.ping': 0,  # Docker is down
        }

    ms.add_metric(keys)

    print "Sending these metrics:"
    print json.dumps(keys, indent=4)
    ms.send_metrics()
    print "\nDone.\n"
