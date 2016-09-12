#!/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4

"""
Script for generating all the folders needed for the shards in the
zagg data folders.
Reads the /etc/openshift_tools/zagg_server.yaml config file and
creates all folders and adds another one (dnd - did not deliver)
where all the faulty yamls should end up

"""

import os
import yaml

CONFIG = yaml.load(file('/etc/openshift_tools/zagg_server.yaml'))
for target in CONFIG['targets']:
    for i in range(0, 256):
        fullpath = os.path.join(target['path'], '{0:02x}'.format(i))
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)
            os.chmod(fullpath, 0o2777)

    os.makedirs(os.path.join(target['path'], 'dnd'))
    os.chmod(os.path.join(target['path'], 'dnd'), 0o2777)
