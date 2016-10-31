#!/usr/bin/python
"""ansible module for rhsm repo management"""
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4

DOCUMENTATION = '''
---
module: aos_rhsm_repos
short_description: this module manages rhsm repositories
description:
- this module manages rhsm repositories
options:
enabled:
  description:
  - list of repo ids to enable. supports *.
  required: false
  default: none
  aliases: []
disabled:
  description:
  - list of repo ids to disable.  supports *.
  required: false
  default: none
  aliases: []
state:
  choices: ['list', 'present']
  description:
  - whether to list or set the repositories.
  required: false
  default: present
  aliases: []
query:
  choices: ['all', 'enabled', 'disabled']
  description:
  - The query type when looking at repositories.
  required: false
  default: all
  aliases: []
'''
EXAMPLES = '''
# perform a list on the enabled repos
- aos_rhsm_repos:
    state: list
    query: enabled
  register: repos

# Set repositories 2 repositories and disable the others.
- aos_rhsm_repos:
    state: present
    enabled:
    - rhel-7-server-rpms
    - rhel-7-server-extras-rpms
    disabled:
    - '*'
'''
import re

RHSM_BIN = '/usr/sbin/subscription-manager'

class RHSMError(Exception):
    """rhsm error"""
    pass

class RHSMRepos(object):
    """simple wrapper class for rhsm repos"""
    def __init__(self, module):
        self.module = module
        self.enabled = module.params['enabled']
        self.disabled = module.params['disabled']

    def set_repositories(self):
        """set the enabled and disabled repositories"""
        cmd = [RHSM_BIN, 'repos']
        if self.disabled:
            cmd.extend(['--disable=%s' % dis for dis in self.disabled])
        # enabled must come last as disable will undo the enabled.
        if self.enabled:
            cmd.extend(['--enable=%s' % ena for ena in self.enabled])

        rcode, out, err = self.module.run_command(cmd)
        if rcode != 0:
            self.module.fail_json(msg={'rc': rcode, 'cmd': cmd, 'err': err})

        return rcode, out, err

    @staticmethod
    def parse_repos(rinput):
        """parse the repo output"""
        all_repos = []
        # split rinput on double new lines
        repos = re.split('\n\n', rinput)
        for idx, repo in enumerate(repos):
            repo.strip()
            if not repo:
                continue

            repo = repo.split('\n')

            # remove the first 3 lines
            if idx == 0:
                repo = repo[3:]

            if len(repo) != 4:
                raise RHSMError('error parsing repositories. repo=%s' % repo)

            all_repos.append({'id': repo[0].split('ID:')[1].strip(),
                              'name': repo[1].split('Name:')[1].strip(),
                              'url': repo[2].split('URL:')[1].strip(),
                              'enabled': int(repo[3].split('Enabled:')[1].strip()) == 1
                             })

        return all_repos


    def query_repos(self, qtype='list'):
        """query for repos"""

        cmd = [RHSM_BIN, 'repos']

        if qtype == 'enabled':
            cmd.append('--list-enabled')
        elif qtype == 'disabled':
            cmd.append('--list-disabled')
        else:
            cmd.append('--list')

        rcode, out, err = self.module.run_command(cmd)
        if rcode != 0:
            self.module.fail_json(msg={'rc': rcode, 'cmd': cmd,
                                       'err': 'Error querying repositories: [%s]' % err,
                                      })

        if 'no available repositories matching' in out:
            return []

        try:
            return RHSMRepos.parse_repos(out)
        except RHSMError as err:
            self.module.fail_json(msg=err)

    def needs_update(self):
        """verify that the enabled repos are enabled"""
        repos = self.query_repos(qtype='enabled')

        # build sets of the repo ids and compare them
        rids = set([rep['id'] for rep in repos])
        ren = set(self.enabled)
        diff = rids - ren
        if diff or ren - rids:
            return True, diff

        return False, repos

    def check_identity(self):
        """verify that this system is entitled"""
        rcode, _, _ = self.module.run_command([RHSM_BIN, 'identity'])
        if rcode != 0:
            self.module.fail_json(msg="command `subscription-manager identity` failed.  exit code non zero.")

    @staticmethod
    def run_ansible(module):
        """run the ansible code"""
        rhsm = RHSMRepos(module)

        # Step 1: verify we are entitled
        rhsm.check_identity()

        # Step 2: if we are state=list, query and return results
        if rhsm.module.params['state'] == 'list':
            repos = rhsm.query_repos(qtype=module.params['query'])

            rhsm.module.exit_json(changed=False, repos=repos)

        # Step 2: if we are state=present, check if we need to update
        elif module.params['state'] == 'present':
            update, repos = rhsm.needs_update()
            # No updates needed
            if update == False:
                module.exit_json(changed=False, repos=repos)

            # Exit if check mode before we make changes
            if module.check_mode:
                module.exit_json(changed=True, repos=repos)

            # Step 3: we need to set our repositories
            rcode, out, err = rhsm.set_repositories()

            # Query the enabled repositories and verify our changes are set.
            update, repos = rhsm.needs_update()

            # Everything went ok, return the enabled repositories
            if not update:
                module.exit_json(changed=True, repos=repos)

            # An error occured while calling set_repositories
            module.fail_json(msg="rhsm repo command failed. Changes not applied.",
                             rcode=rcode,
                             stdout=out,
                             stderr=err)

        module.fail_json(msg="unsupported state.")

def main():
    """Create the ansible module and run the ansible code"""
    module = AnsibleModule(
        argument_spec=dict(
            enabled=dict(default=None, type='list'),
            disabled=dict(default=None, type='list'),
            state=dict(default='present', choices=['list', 'present']),
            query=dict(default='all', choices=['all', 'enabled', 'disabled']),
        ),
        supports_check_mode=True
    )

    # call the ansible function
    RHSMRepos.run_ansible(module)

if __name__ == '__main__':
# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import
# import module snippets
    from ansible.module_utils.basic import *
    main()
