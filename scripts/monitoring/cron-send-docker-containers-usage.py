#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

'''
    docker container resource usage sender
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name
# pylint flags import errors, as the bot doesn't know out openshift-tools libs
# pylint: disable=import-error


from docker import AutoVersionClient
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.hawk_sender import HawkSender
from openshift_tools.monitoring.dockerutil import DockerUtil
import os
import yaml
import re
import sre_constants


ZBX_DOCKER_DISC_KEY = "disc.docker.container"
ZBX_DOCKER_DISC_MACRO = "#CTR_NAME"


ZBX_CTR_BASE_KEY = "disc.docker.container"

ZBX_CTR_CPU_BASE_KEY = "%s.cpu" % ZBX_CTR_BASE_KEY
ZBX_CTR_CPU_USED_PCT_KEY = "%s.used_pct" % ZBX_CTR_CPU_BASE_KEY

ZBX_CTR_MEM_BASE_KEY = "%s.mem" % ZBX_CTR_BASE_KEY
ZBX_CTR_MEM_USED_KEY = "%s.used" % ZBX_CTR_MEM_BASE_KEY
ZBX_CTR_MEM_LIMIT_KEY = "%s.limit" % ZBX_CTR_MEM_BASE_KEY
ZBX_CTR_MEM_LIMIT_USED_PCT_KEY = "%s.limit_used_pct" % ZBX_CTR_MEM_BASE_KEY
ZBX_CTR_MEM_FAILCNT_KEY = "%s.failcnt" % ZBX_CTR_MEM_BASE_KEY


class DockerContainerUsageCli(object):
    ''' This is the class that actually pulls eveyrthing together into a cli script.
    '''
    def __init__(self, config_file=None):
        if not config_file:
            self.config_file = '/etc/openshift_tools/container_metrics.yml'
        else:
            self.config_file = config_file

        self.config = None

        self.parse_config()

        self.cli = AutoVersionClient(base_url='unix://var/run/docker.sock', timeout=120)
        self.docker_util = DockerUtil(self.cli)
        self.zagg_sender = ZaggSender(verbose=True)
        self.hawk_sender = HawkSender(verbose=True)

    def parse_config(self):
        """ parse config file """

        if not self.config:
            if not os.path.exists(self.config_file):
                raise IOError(self.config_file + " does not exist.")

            self.config = yaml.load(file(self.config_file))

    def format_ctr_name(self, ctr_name):
        ''' Takes a container name and if there's a name_format_regex specified, it applies it '''
        for item in self.config['usage_checks']:
            name_match_regex = item['name_match_regex']

            if item.has_key('name_format_regex') and re.match(name_match_regex, ctr_name):
                try:
                    name_format_regex = item['name_format_regex']
                    new_name = re.sub(name_match_regex, name_format_regex, ctr_name)
                    return new_name
                except sre_constants.error as ex:
                    # Just use the full name (we don't want to die because of name formatting)
                    print "\nError: %s: [%s]. Using full name [%s].\n" % (ex.message, name_format_regex, ctr_name)
                    return ctr_name

        return ctr_name

    def main(self):
        ''' The main entrypoint of the cli '''
        ctr_regexes = [uchk['name_match_regex'] for uchk in self.config['usage_checks']]
        use_cgroups = self.config.get('use_cgroups', False)

        ctrs = self.docker_util.get_ctrs_matching_names(ctr_regexes)


        for ctr_name, ctr in ctrs.iteritems():
            (cpu_stats, mem_stats) = self.docker_util.get_ctr_stats(ctr, use_cgroups=use_cgroups)

            formatted_ctr_name = self.format_ctr_name(ctr_name)

            # Add the container hostnames as macros for the dynamic item.
            self.zagg_sender.add_zabbix_dynamic_item(ZBX_DOCKER_DISC_KEY, ZBX_DOCKER_DISC_MACRO,
                                                     [formatted_ctr_name])
            #TODO: implement self.hawk_sender.add_zabbix_dynamic_item                                         
            data = {
                '%s[%s]' % (ZBX_CTR_CPU_USED_PCT_KEY, formatted_ctr_name): cpu_stats.used_pct,
                '%s[%s]' % (ZBX_CTR_MEM_USED_KEY, formatted_ctr_name): mem_stats.used,
                '%s[%s]' % (ZBX_CTR_MEM_LIMIT_KEY, formatted_ctr_name): mem_stats.limit,
                '%s[%s]' % (ZBX_CTR_MEM_LIMIT_USED_PCT_KEY, formatted_ctr_name): mem_stats.limit_used_pct,
                '%s[%s]' % (ZBX_CTR_MEM_FAILCNT_KEY, formatted_ctr_name): mem_stats.failcnt,
            }

            print "%s:" % formatted_ctr_name
            for k, v in data.iteritems():
                print "  %s: %s" % (k, v)
            print

            self.zagg_sender.add_zabbix_keys(data)
            self.hawk_sender.add_zabbix_keys(data)

        # Actually send the metrics
        self.zagg_sender.send_metrics()
        self.hawk_sender.send_metrics()


if __name__ == "__main__":
    dcuc = DockerContainerUsageCli()
    dcuc.main()
