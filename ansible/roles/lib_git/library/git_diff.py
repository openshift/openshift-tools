#!/usr/bin/env python
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|
'''
   OpenShiftCLI class that wraps the oc commands in a subprocess
'''
# pylint: disable=too-many-lines

import os
import subprocess

class GitCLIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class GitCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self,
                 path,
                 verbose=False):
        ''' Constructor for GitCLI '''
        self.path = path
        self.verbose = verbose

    def _add(self, files_to_add=None):
        ''' git add '''

        cmd = ["add"]

        if files_to_add:
            cmd.extend(files_to_add)
        else:
            cmd.append('.')

        results = self.git_cmd(cmd)

        return results

    def _commit(self, msg):
        ''' git commit with message '''

        cmd = ["commit", "-m", msg]

        results = self.git_cmd(cmd)

        return results

    def _status(self, porcelain=False, show_untracked=True):
        ''' Do a git status '''

        cmd = ["status"]
        if porcelain:
            cmd.append('--porcelain')

        if show_untracked:
            cmd.append('--untracked-files=normal')
        else:
            cmd.append('--untracked-files=no')

        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def _checkout(self, branch):
        ''' Do a git checkout to <branch> '''

        cmd = ["checkout", branch]
        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def _get_current_branch(self):
        ''' Do a git checkout to <branch> '''

        cmd = ["describe", "--contains", "--all", "HEAD"]
        results = self.git_cmd(cmd, output=True, output_type='raw')
        results['results'] = results['results'].rstrip()

        return results

    def _merge(self, merge_id):
        ''' Do a git checkout to <branch> '''

        cmd = ["merge", merge_id]
        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def _push(self, remote, src_branch, dest_branch):
        ''' Do a git checkout to <branch> '''

        push_branches = src_branch + ":" + dest_branch

        cmd = ["push", remote, push_branches]
        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def _remote_update(self):
        ''' Do a git remote update '''

        cmd = ["remote", "update"]
        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def _diff(self, diff_branch):
        ''' Do a git diff diff_branch'''

        cmd = ["diff", diff_branch]
        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def _rebase(self, rebase_branch):
        ''' Do a git rebase rebase_branch'''

        cmd = ["rebase", rebase_branch]
        results = self.git_cmd(cmd, output=True, output_type='raw')

        return results

    def git_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for git '''
        cmds = ['/usr/bin/git']

        cmds.extend(cmd)

        rval = {}
        results = ''
        err = None

        if self.verbose:
            print ' '.join(cmds)

        proc = subprocess.Popen(cmds,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        rval = {"returncode": proc.returncode,
                "results": results,
                "cmd": ' '.join(cmds),
               }

        if proc.returncode == 0:
            if output:
                if output_type == 'json':
                    try:
                        rval['results'] = json.loads(stdout)
                    except ValueError as err:
                        if "No JSON object could be decoded" in err.message:
                            err = err.message
                elif output_type == 'raw':
                    rval['results'] = stdout

            if self.verbose:
                print stdout
                print stderr

            if err:
                rval.update({"err": err,
                             "stderr": stderr,
                             "stdout": stdout,
                             "cmd": cmds
                            })

        else:
            rval.update({"stderr": stderr,
                         "stdout": stdout,
                         "results": {},
                        })

        return rval

class GitDiff(GitCLI):
    ''' Class to wrap the git merge line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 branch,
                 diff_branch,
                ):
        ''' Constructor for GitDiff '''
        super(GitDiff, self).__init__(path)
        self.path = path
        self.branch = branch
        self.diff_branch = diff_branch
        self.debug = []

        os.chdir(path)

    def checkout_branch(self):
        ''' check out the desired branch '''

        current_branch_results = self._get_current_branch()

        if current_branch_results['results'] == self.branch:
            return True

        current_branch_results = self._checkout(self.branch)

        self.debug.append(current_branch_results)
        if current_branch_results['returncode'] == 0:
            return True

        return False

    def diff(self):
        '''perform a git diff '''

        if self.checkout_branch():
            diff_results = self._diff(self.diff_branch)
            return diff_results

def main():
    '''
    ansible git module for merging
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='list', type='str', choices=['list']),
            path=dict(default=None, required=True, type='str'),
            branch=dict(default=None, required=True, type='str'),
            diff_branch=dict(default=None, required=True, type='str'),
            fail_on_diff=dict(default=False, required=False, type='bool'),
        ),
        supports_check_mode=False,
    )
    git = GitDiff(module.params['path'],
                  module.params['branch'],
                  module.params['diff_branch'],
                 )

    state = module.params['state']
    fail_on_diff = module.params['fail_on_diff']

    if state == 'list':
        results = git.diff()

        if fail_on_diff:
            if results['results']:
                module.exit_json(failed=True, changed=False, results=results, state="list")

        module.exit_json(changed=False, results=results, state="list")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
#if __name__ == '__main__':
#    main()
from ansible.module_utils.basic import *

main()
