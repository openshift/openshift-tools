#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
See Ansible Module Documentation (Below)
'''
import re
import iniparse

DOCUMENTATION = '''
---
module: yum_repo_exclude
short_description: manage packages on a YUM repo's exclude line
description:
     - Add package names or patterns to a YUM repository configuration's exclude line
options:
            name=dict(required=True),
            repo=dict(required=True),
            patterns=dict(required=True, type='list'),
            state=dict(required=False, default='present', choices=['present', 'absent']),
  name:
    description:
      - Filename where the repository configuration exists
    required: true
  state:
    description:
      - One of 'present', 'absent'. If 'present', patterns are added (if necessary). If 'absent', patterns are removed (if necessary).
    required: true
    default: present
  repo:
    description:
      - The name of the repository
    required: true
  patterns:
    description:
      - A list of package names and/or package patterns
    required: true
author:
    - "Joel Smith (joelsmith@redhat.com)"
'''

EXAMPLES = '''
tasks:
- name: Don't install foo from repo bar
  yum_repo_exclude:
    name: /etc/yum.repos.d/bar.repo
    repo: bar
    patterns: [ foo ]
- name: Stop excluding baz and qux-* from repo bar
  yum_repo_exclude:
    name: /etc/yum.repos.d/bar.repo
    repo: bar
    patterns: [ baz, qux-* ]
    state: absent
'''

class YumRepoExcludeError(Exception):
    '''All YumRepoExclude methods throw this exception when errors occur'''
    def __init__(self, msg):
        super(YumRepoExcludeError, self).__init__(msg)
        self.msg = msg

class YumRepoExclude(object):
    '''A YUM repo's exclude option'''

    def __init__(self, filename, repo):
        '''Create an exclude'''
        self.filename = filename
        self.repo = repo

    def get(self):
        '''Get the current exclude value'''
        ini = None
        with open(self.filename) as repofile:
            ini = iniparse.INIConfig(repofile)
        repoobj = ini[self.repo]
        if not getattr(repoobj, "__getitem__", None):
            raise YumRepoExcludeError("Repository {} not found in file {}".format(self.repo, self.filename))
        current = repoobj["exclude"]
        if getattr(current, "__getitem__", None):
            return re.split(r'\s+', current)
        return list()

    def set(self, patterns):
        '''Update the exclude value'''
        with open(self.filename, 'r+') as repofile:
            ini = iniparse.INIConfig(repofile)
            repoobj = ini[self.repo]
            if not getattr(repoobj, "__getitem__", None):
                raise YumRepoExcludeError("Repository {} not found in file {}".format(self.repo, self.filename))
            repoobj["exclude"] = " ".join(patterns)
            repofile.seek(0)
            repofile.write(re.sub(r'^exclude += +', 'exclude=', str(ini), flags=re.M))
            repofile.truncate()

def main():
    '''Ansible module to add/remove packages or patterns from a YUM repo's exclude line'''
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            repo=dict(required=True),
            patterns=dict(required=True, type='list'),
            state=dict(required=False, default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )
    name = module.params['name']
    repo = module.params['repo']
    patterns = module.params['patterns']
    state = module.params['state']

    changed = False
    yumrepo = YumRepoExclude(name, repo)

    try:
        current = set(yumrepo.get())
        if state == 'absent':
            expected = current - set(patterns)
        elif state == 'present':
            expected = current | set(patterns)

        if current != expected:
            yumrepo.set(expected)
            current = set(yumrepo.get())
            if current == expected:
                changed = True
            else:
                module.fail_json(msg="Update to repo {} from {} failed. Expected {}, got {}".format(repo, name,
                                                                                                    expected, current))

    except YumRepoExcludeError as ex:
        module.fail_json(msg=ex.msg)

    return module.exit_json(changed=changed)


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, wrong-import-position
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
