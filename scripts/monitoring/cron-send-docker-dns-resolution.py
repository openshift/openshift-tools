#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker container DNS tester
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


import time
from docker import AutoVersionClient
from docker.errors import APIError
# Jenkins doesn't have our tools which results in import errors
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.hawk_sender import HawkSender

ZBX_KEY = "docker.container.dns.resolution"

if __name__ == "__main__":
    cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
    container = cli.create_container(image='docker-registry.ops.rhcloud.com/ops/oso-rhel7-host-monitoring',
                                     command='getent hosts redhat.com')
    cli.start(container=container.get('Id'))
    exit_code = cli.wait(container)

    for i in range(0, 3):
        try:
            cli.remove_container(container.get('Id'))
            break
        except APIError:
            print "Error while cleaning up container."
            time.sleep(5)

    zs = ZaggSender()
    hs = HawkSender()
    zs.add_zabbix_keys({ZBX_KEY: exit_code})
    hs.add_zabbix_keys({ZBX_KEY: exit_code})

    print "Sending these metrics:"
    print ZBX_KEY + ": " + str(exit_code)
    zs.send_metrics()
    hs.send_metrics()
    print "\nDone.\n"
