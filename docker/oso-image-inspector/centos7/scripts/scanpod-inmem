#!/usr/bin/python
#pylint: disable=invalid-name

'''A scanner of processes running in pods on an OpenShift node'''

#TODO: Allow user to select namespaces, pods, containers, and/or processes for scanning
#TODO: Support signature whitelists
#TODO: Cache results of long-running processes
#TODO: Use logging for error messages and debug

import os
import subprocess
import re
import sys
import time
from collections import namedtuple
import yaml
import requests
#pylint: disable=import-error
import clamd
#pylint: enable=import-error

NODECFGFILE = "/etc/origin/node/node-config.yaml"
URL = 'https://openshift.default.svc.cluster.local/api/v1/pods'

# A device number and an inode will uniquely identify a file. Use this
# tuple as a dictionary key to map from a scanned file to its result
FileTuple = namedtuple('FileTuple', 'dev inode')

# given a container ID, get the mount namespace inode that its processes use
def get_mnt_ns(containerid):
    '''Get the mount namespace inode number for a given container ID'''
    if not containerid:
        return None
    if containerid.startswith('docker://'):
        containerid = containerid[len('docker://'):]
        # get the pid of the main process in the container
        pid = subprocess.check_output(['/host/usr/bin/docker', 'inspect', '--format={{.State.Pid}}', containerid]).rstrip()
        try:
            # get and return the inode of the process's mount namespace. All other processes in the container will
            # have the same mount namespace (assuming non-privileged containers that don't have CAP_SYS_ADMIN and
            # can't call setns()).
            return os.stat('/host/proc/{pid}/ns/mnt'.format(pid=pid)).st_ino
        except OSError:
            # The process has probably gone away
            return None
    else:
        raise ValueError("Unrecognized containerID: {id}".format(id=containerid))

def scanpid(pid, scancache, clam):
    '''Scan the executable bits of the process corresponding to pid.'''
    retval = {}
    try:
        with open('/host/proc/{pid}/maps'.format(pid=pid), 'r') as maps:
            # iterate over all executable memory-mapped files (generally binaries and libraries)
            for line in maps:
                match = re.search(r'^(?P<name>[^ ]*) [r-][w-]x[ps-]', line)
                # not an executable segment - skip it
                if not match:
                    continue
                toscan = '/host/proc/{pid}/map_files/{range}'.format(pid=pid, range=match.group('name'))
                try:
                    statval = os.stat(toscan)
                # if the process goes away while we're scanning, we'll hit this exception. Also,
                # there are plenty of entries in /proc/<pid>/maps that don't have a corresponding
                # /proc/<pid>/map_files/* file
                except OSError:
                    continue
                filetuple = FileTuple(statval.st_dev, statval.st_ino)
                result = scancache.get(filetuple)
                # see if we've already scanned this file, whether when we scanned other entries in
                # this process, other processes in this container, or processes in other containers
                # that share the same device (like, if they have the same base image layer).
                if not result:
                    try:
                        with open(toscan, 'r') as stream:
                            scanned = clam.fdscan('fd', stream.fileno())
                    except IOError:
                        # if the process has gone away, we won't be able to open toscan. No worries
                        continue
                # for any non-'OK' results, get the container-local file path and return it with the results
                if result != 'OK':
                    try:
                        retval[os.readlink(toscan)] = result
                    except OSError:
                        # no worries if we tried to open it and failed. The process has probably gone away
                        pass

    except OSError as err:
	print("OS error: {0}".format(err))
        pass

    except IOError as err:
	print("IO error: {0}".format(err))
        pass

    return retval

def scanall(mntns, namespace, podname, container, scancache):
    '''Scan all processes in a given mount namespace'''
    clam = clamd.ClamdUnixSocket(path='/host/host/var/run/clamd.scan/clamd.sock')
    # iterated over all running processes
    for pid in [pid for pid in os.listdir('/host/proc') if pid.isdigit()]:
        try:
            # get the process's mount namespace
            this_mntns = os.stat('/host/proc/{pid}/ns/mnt'.format(pid=pid)).st_ino
        except OSError:
            # no worries if we tried to open it and failed. The process has probably gone away
            pass
        # ignore processes that don't have the requested mount namespace
        if this_mntns == mntns:
            # scan the process and iterate over the results.
            for fname, found in scanpid(pid, scancache, clam).iteritems():
                print "Found in {ns}/{pod}/{container}:{file}: {result}".format(ns=namespace, pod=podname,
                                                                                container=container,
                                                                                file=fname, result=found)

def main():
    '''Scan all processes running in a pod on a node'''
    # A map of FileTuple to results
    scancache = {}
    # Get nodeName from the node config file
    node = None
    with open(NODECFGFILE, 'r') as stream:
        nodecfg = yaml.load(stream)
        node = nodecfg.get('nodeName')
    if not node:
        raise ValueError('Unable to get key "nodeName" from node config file {conffile}'.format(conffile=NODECFGFILE))

    # Get details of pods running on this node (like "oadm manage-node --lits-pods")
    # Retry up to 7 times with exponential back-off
    certbase = '/host/etc/origin/node/system:node:{nodename}'.format(nodename=node)
    for i in range(1, 8):
        response = requests.get(URL, params={'fieldSelector': "spec.nodeName={nodename}".format(nodename=node)},
                                verify="/host/etc/pki/ca-trust/source/anchors/openshift-ca.crt",
                                cert=(certbase + '.crt', certbase + '.key'))
        if response.ok:
            break
        if i < 7:
            print "Request failed: {error}, retrying in {seconds} seconds".format(error=response.text.rstrip(),
                                                                                  seconds=2**i)
            time.sleep(2**i)
        else:
            print "Request failed: {error}".format(error=response.text.rstrip())
            sys.exit(1)

    # iterate over all the pods on the node
    for pod in response.json().get('items', []):
        # iterate over all the containers in the pod
        for cstatus in pod.get('status', {}).get('containerStatuses', []):
            # ignore containers in the terminated state
            if not cstatus.get('state', {}).get('terminated'):
                # get the mount namespace for the container, which we'll use to find all
                # other proecesses in the same container
                mntns = get_mnt_ns(cstatus.get('containerID', ''))
                if mntns:
                    # scan all processes in a given mount namespace
                    scanall(mntns, pod['metadata']['namespace'], pod['metadata']['name'], cstatus['name'], scancache)

if __name__ == "__main__":
    main()
