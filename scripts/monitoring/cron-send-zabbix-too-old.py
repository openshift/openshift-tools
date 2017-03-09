#!/usr/bin/python

'''
This script will download the yum repository metadata for the
Zabbix 3.0 (LTS) branch and determine the latest version of the
zabbix-server-mysql package. It will then find version of the
same RPM as deployed in the environment. It will determine
how many versions old the running version is and send that
value to Zabbix.
'''

#pylint: disable=invalid-name

from __future__ import print_function
import argparse
import urllib
import gzip
import io
import os
import rpm
import lxml.etree
import lxml.objectify
import subprocess
#pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender
#pylint: enable=import-error

REPOURL = 'https://repo.zabbix.com/zabbix/3.0/rhel/7/x86_64/repodata/primary.xml.gz'
NS = 'new-monitoring'
DC = 'oso-rhel7-zabbix-server'
RPMNAME = 'zabbix-server-mysql'
KEY = 'zabbix.software.version.disparity'
SENDER_HOST = 'Zabbix server'

# stolen from https://wiki.python.org/moin/HowTo/Sorting
# This is a shim so that we can use rpm.labelCompare with sorted()
def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    # pylint: disable=too-few-public-methods
    class Key(object):
        'A key class for sorted() that wraps a legacy cmp function'
        def __init__(self, obj, *args):
            del args
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    # pylint: enable=too-few-public-methods
    return Key

def rpmcmp(aaa, bbb):
    'Compare the RPM versions of two RPM XML entries'
    return rpm.labelCompare((aaa.get('epoch'), aaa.get('ver'), aaa.get('rel')),
                            (bbb.get('epoch'), bbb.get('ver'), bbb.get('rel')))

def parse_args():
    ''' parse the args from the cli '''
    parser = argparse.ArgumentParser(description='Count how many versions behind Zabbix is.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Print more information.')

    return parser.parse_args()

def send(values, options):
    ''' Send any passed metrics values '''

    if options.verbose:
        print('Sending values:', values)

    sender = MetricSender(host=SENDER_HOST, verbose=options.verbose, debug=options.verbose)
    for key in values:
        sender.add_metric({key: values[key]})
    sender.send_metrics()

def verbose_print(options, *args):
    'Only print messages when verbose option is enabled'
    if options.verbose:
        print(*args)

def main():
    'Compare latest version in a repository one installed in the container'

    opts = parse_args()

    verbose_print(opts, "Fetching repo metadata from {0}". format(REPOURL))
    zipped_xml = urllib.urlopen(REPOURL)
    unzipped_xml = gzip.GzipFile(fileobj=io.BytesIO(zipped_xml.read()), mode='rb')

    root = lxml.etree.parse(unzipped_xml)
    # We don't care about namespaces and they make things more complicated, so remove them
    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'):
            continue
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    lxml.objectify.deannotate(root, cleanup_namespaces=True)

    # we want the version element which is the child of any package
    # element having a child element <name> with a value of RPMNAME
    versions = root.xpath("./package[name = '{0}']/version".format(RPMNAME))
    # Sort the versions using RPM verion sorting rules
    sorted_versions = sorted(versions, reverse=True, key=cmp_to_key(rpmcmp))
    if len(sorted_versions) == 0:
        print("No latest version determined from {0}. Bailing out.".format(REPOURL))
        exit(1)
    # Get the latest one (which will be the first item in the list
    newest = next(iter(sorted_versions or []), None)
    if newest is not None:
        verbose_print(opts, "Newest version of {0}: {1}-{2}".format(RPMNAME, newest.get('ver'), newest.get('rel')))
    else:
        verbose_print(opts, "Unable to determine newest version of {0} from repo metadata".format(RPMNAME))
    verbose_print(opts, "Looking for a running pod via the deployment config {0}/{1}". format(NS, DC))

    env_copy = os.environ.copy()
    env_copy['KUBECONFIG'] = '/tmp/admin.kubeconfig'
    podname = subprocess.check_output(['oc', 'get', 'pods', '-n', NS, '-l', 'deploymentconfig='+DC, '-o', 'name'],
                                      env=env_copy)
    # we only need one, so if there was more than one, take the first one
    podname = next(iter(podname.split('\n')))
    if podname.startswith('pod/'):
        podname = podname[4:]
    if not podname:
        verbose_print(opts, "No pod found running in DC {0}/{1}. Bailing out.". format(NS, DC))
        exit(1)
    verbose_print(opts, "Looking at installed version of {0} in pod {1}/{2}". format(RPMNAME, NS, podname))
    installed = subprocess.check_output(['oc', 'exec', '-n', NS, podname, '--',
                                         'rpm', '-q', '--queryformat', '%{VERSION}-%{RELEASE}', RPMNAME], env=env_copy)
    verbose_print(opts, "Current version of {0} in pod: {1}".format(RPMNAME, installed))
    behind = 0
    if installed:
        version, release = installed.split('-')
        for ver in sorted_versions:
            if ver.get('ver') == version and ver.get('rel') == release:
                break
            behind += 1
    verbose_print(opts, "Behind by {0} versions. Sending.".format(behind))
    values = {}
    values[KEY] = behind
    send(values, opts)

if __name__ == '__main__':
    main()
