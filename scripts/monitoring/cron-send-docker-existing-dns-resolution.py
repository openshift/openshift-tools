#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker container DNS tester for all currently running containers
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name


from docker import AutoVersionClient
from docker.errors import APIError
from openshift_tools.monitoring.zagg_sender import ZaggSender

ZBX_KEY = "docker.container.existing.dns.resolution.failed"
CMD_NOT_FOUND = -1

if __name__ == "__main__":
    cli = AutoVersionClient(base_url='unix://var/run/docker.sock')
    bad_dns_count = 0

    for ctr in cli.containers():
        try:
            exec_id = cli.exec_create(container=ctr['Id'], cmd="getent hosts redhat.com")
            results = cli.exec_start(exec_id=exec_id)
            exit_code = cli.exec_inspect(exec_id)['ExitCode']
        except APIError:
            # could race from getting a container list and the container exiting
            # before we can exec on it, so just ignore exited containers
            continue

        if exit_code == CMD_NOT_FOUND:
            continue

        print "Container: " + ctr['Image']
        print results
        print "Exit Code: " + str(exit_code) + "\n"

        if exit_code != 0:
            bad_dns_count += 1

    zs = ZaggSender()
    zs.add_zabbix_keys({ZBX_KEY: bad_dns_count})

    print "Sending these metrics:"
    print ZBX_KEY + ": " + str(bad_dns_count)
    zs.send_metrics()
    print "\nDone.\n"
