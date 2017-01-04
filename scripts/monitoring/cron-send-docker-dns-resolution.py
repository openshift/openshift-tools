#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker container DNS tester
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


import time
import os
from docker import AutoVersionClient
from docker.errors import APIError
# Jenkins doesn't have our tools which results in import errors
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender

ZBX_KEY = "docker.container.dns.resolution"

if __name__ == "__main__":
    cli = AutoVersionClient(base_url='unix://var/run/docker.sock')

    container_id = os.environ['container_uuid']

    container = cli.create_container(image=cli.inspect_container(container_id)['Image'],
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

    ms = MetricSender()
    ms.add_metric({ZBX_KEY: exit_code})

    print "Sending these metrics:"
    print ZBX_KEY + ": " + str(exit_code)
    ms.send_metrics()
    print "\nDone.\n"
