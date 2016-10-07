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

    # Pylint allows only 5 arguments to be passed.
    # pylint: disable=too-many-arguments
    def _commit(self, msg):
        ''' git commit with message '''
        cmd = ["add", "."]
        results = self.git_cmd(cmd)

        if results['returncode'] != 0:
            return results

        cmd = ["commit", "-am", msg]

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

class GitPush(GitCLI):
    ''' Class to wrap the git merge line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 remote,
                 src_branch,
                 dest_branch):
        ''' Constructor for GitPush '''
        super(GitPush, self).__init__(path)
        self.path = path
        self.remote = remote
        self.src_branch = src_branch
        self.dest_branch = dest_branch
        self.debug = []

        os.chdir(path)

    def checkout_branch(self):
        ''' check out the desired branch '''

        current_branch_results = self._get_current_branch()

        if current_branch_results['results'] == self.src_branch:
            return True

        current_branch_results = self._checkout(self.src_branch)

        self.debug.append(current_branch_results)
        if current_branch_results['returncode'] == 0:
            return True

        return False

    def remote_update(self):
        ''' update the git remotes '''

        remote_update_results = self._remote_update()

        self.debug.append(remote_update_results)
        if remote_update_results['returncode'] == 0:
            return True

        return False

    def need_push(self):
        ''' checks to see if push is needed '''

        git_status_results = self._status(show_untracked=False)

        self.debug.append(git_status_results)
        status_msg = "Your branch is ahead of '%s" %self.remote

        if status_msg in git_status_results['results']:
            return True

        return False

    def push(self):
        '''perform a git push '''

        if not self.src_branch or not self.dest_branch or not self.remote:
            return {'returncode': 1,
                    'results':
                    'Invalid variables being passed in. Please investigate remote, src_branc, and/or dest_branch',
                   }

        if self.checkout_branch():
            if self.remote_update():
                if self.need_push():
                    push_results = self._push(self.remote, self.src_branch, self.dest_branch)
                    push_results['debug'] = self.debug

                    return push_results
                else:
                    return {'returncode': 0,
                            'results': {},
                            'no_push_needed': True
                           }

        return {'returncode': 1,
                'results': {},
                'debug': self.debug
               }

def main():
    '''
    ansible git module for merging
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str', choices=['present']),
            path=dict(default=None, required=True, type='str'),
            remote=dict(default=None, required=True, type='str'),
            src_branch=dict(default=None, required=True, type='str'),
            dest_branch=dict(default=None, required=True, type='str'),
        ),
        supports_check_mode=False,
    )
    git = GitPush(module.params['path'],
                  module.params['remote'],
                  module.params['src_branch'],
                  module.params['dest_branch'])

    state = module.params['state']

    if state == 'present':
        results = git.push()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        if results.has_key('no_push_needed'):
            module.exit_json(changed=False, results=results, state="present")

        module.exit_json(changed=True, results=results, state="present")

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
