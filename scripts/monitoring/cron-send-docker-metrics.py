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
        #cli_storage = Client(base_url='unix://var/run/docker.sock')
        du = DockerUtil(cli)
        exited_containers = cli.containers(quiet=True, filters={'status':'exited'}) #get all the exited container
        dead_containers = cli.containers(all=True, quiet=True, filters={'status':'dead'}) #get all the exited container
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
            'docker.containers.exited':len(exited_containers),
            'docker.containers.dead':len(dead_containers)
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
    #start auto-heal

    if int(du_dds.data_space_percent_available) < 50:
        print 'Docker has less than 50% storage avaiable. Attempting to clean up space.'
        print '***********************************'
        #clean the exited containers
        for container in exited_containers:
            print '*******start cleaning**************'
            print 'the container id is :', container['Id']
            #get the info
            exited_container = cli.containers(all=True, filters={'id':container['Id']})
            #print Deadcontainer
            if len(exited_container) == 1:
                print 'the status of the container is :', exited_container[0]['Status']
                if exited_container[0]['Status'].find('Exited') != -1:
                    #do the remove step
                    print 'status confirmed :', exited_container[0]['Status']
                    try:
                        #cli.remove_container(container=container['Id'])
                        print 'done this container'
                    except Exception:
                        print 'something wrong during the remote of the container'
            else:
                print 'container not exist'
        #clean the dead containers
        for container in dead_containers:
            print '*******start cleaning**************'
            print 'the container id is :', container['Id']
            #get the info
            dead_container = cli.containers(all=True, filters={'id':container['Id']})
            #print Deadcontainer
            if len(dead_container) == 1:
                print 'the status of the container is :', dead_container[0]['Status']
                if dead_container[0]['Status'].find('Dead') != -1:
                    #do the remove step
                    print 'status confirmed :', dead_container[0]['Status']
                    try:
                        #cli.remove_container(container=container['Id'])
                        print 'done this container'
                    except Exception:
                        print 'something wrong during the remote of the container'

            else:
                print 'container not exist'
    else:
        print 'Docker storage has more than 50% available. Skipping autoheal to clean up space', int(du_dds.data_space_percent_available)
