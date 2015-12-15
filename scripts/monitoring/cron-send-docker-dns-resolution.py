#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker container DNS tester
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


from docker import AutoVersionClient
from openshift_tools.monitoring.zagg_sender import ZaggSender

ZBX_KEY = "docker.container.dns.resolution"

if __name__ == "__main__":
    cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
    container = cli.create_container(image='rhel7:latest', command='getent hosts google.com')
    cli.start(container=container.get('Id'))
    exit_code = cli.wait(container)
    cli.remove_container(container.get('Id'))

    zs = ZaggSender()
    zs.add_zabbix_keys({ZBX_KEY: exit_code})

    print "Sending these metrics:"
    print ZBX_KEY + ": " + str(exit_code)
    zs.send_metrics()
    print "\nDone.\n"
