#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker info data gatherer
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


from docker import AutoVersionClient
from docker import Client
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
        cli_storage = Client(base_url='unix://var/run/docker.sock')
        du = DockerUtil(cli)
        Deadcontainers = cli_storage.containers(quiet=True,filters={'status':'exited'}) #get all the exited container
        du_dds = du.get_disk_usage()
        print "data_space:",du_dds.data_space_percent_available
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
    
    #start auto-heal 

    #Deadcontainer = cli_storage.containers(filters={'id':'bf34a7c35b907c1f3047321b3073aa74f16957c2505af3644c2c1e7bb976bd78'})
    #print '******************************8'
    #print Deadcontainer[0]['Status']
    print '***********************************'
    if int(du_dds.data_space_percent_available) < 50:
        print 'less than 50'
        #print Deadcontainers
        #remote those dead contaners
        #check the status before remote(double check)
        for container in Deadcontainers:
            print container['Id']
            #get the info
            Deadcontainer = cli_storage.containers(all=True,filters={'id':container['Id']})
            #print Deadcontainer
            if len(Deadcontainer) == 1:
                print '******************************'
                print Deadcontainer[0]['Status']
                print '***********************************'
                if Deadcontainer[0]['Status'].find('Exited') != -1:
                    #do the remove step
                    print Deadcontainer[0]['Status'].find('Exited')
                    #cli_storage.remove_container(container=container['Id'])
            else:
                print 'container not exist'
    else:
        print 'not less',int(du_dds.data_space_percent_available)
