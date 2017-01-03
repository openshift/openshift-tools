#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    Report time to execute 'docker info'
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
import time

if __name__ == "__main__":
    keys = None
    mts = MetricSender()
    try:
        cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
        du = DockerUtil(cli, max_wait=360)

        # Wait up to 6 minutes
        time_start = time.time()
        du.get_disk_usage()
        time_stop = time.time()
        elapsed_ms = int((time_stop - time_start) * 1000)

        keys = {
            'docker.info_elapsed_ms': elapsed_ms
        }
    except (DockerException, TimeoutException) as ex:
        print "\nERROR talking to docker: %s\n" % ex.message
        keys = {
            'docker.info_elapsed_ms': 360000 # 360000 = 6 minutes
        }

    mts.add_metric(keys)

    print "Sending these metrics:"
    print json.dumps(keys, indent=4)
    mts.send_metrics()
    print "\nDone.\n"
