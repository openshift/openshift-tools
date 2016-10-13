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

class GitCommit(GitCLI):
    ''' Class to wrap the git command line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 msg,
                 path,
                 commit_files):
        ''' Constructor for GitCommit '''
        super(GitCommit, self).__init__(path)
        self.path = path
        self.msg = msg
        self.commit_files = commit_files
        self.debug = []

        os.chdir(path)

        self.status_results = self._status(porcelain=True)
        self.debug.append(self.status_results)

    def get_files_to_commit(self):
        ''' do we have files to commit?'''

        files_found_to_be_committed = []

        # get the list of files that changed according to git status
        git_status_out = self.status_results['results'].split('\n')
        git_status_files = []

        #clean up the data
        for line in git_status_out:
            file_name = line[3:]
            if "->" in line:
                file_name = file_name.split("->")[-1].strip()
            git_status_files.append(file_name)

        # Check if the files to be commited are in the git_status_files
        for file_name in self.commit_files:
            file_name = str(file_name)
            for status_file in git_status_files:
                if status_file.startswith(file_name):
                    files_found_to_be_committed.append(status_file)

        return files_found_to_be_committed

    def have_commits(self):
        ''' do we have files to commit?'''

        # test the results
        if self.status_results['results']:
            return True

        return False

    def commit(self):
        '''perform a git commit '''

        if self.have_commits():
            add_results = None
            if self.commit_files:
                files_to_add = self.get_files_to_commit()
                if files_to_add:
                    add_results = self._add(files_to_add)
            else:
                add_results = self._add()

            if add_results:
                self.debug.append(add_results)
                commit_results = self._commit(self.msg)
                commit_results['debug'] = self.debug

                return commit_results

        return {'returncode': 0,
                'results': {},
                'no_commits': True,
                'debug': self.debug
               }

def main():
    '''
    ansible git module for committting
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str', choices=['present']),
            msg=dict(default=None, required=True, type='str'),
            path=dict(default=None, required=True, type='str'),
            commit_files=dict(default=None, required=False, type='list'),
        ),
        supports_check_mode=False,
    )
    git = GitCommit(module.params['msg'],
                    module.params['path'],
                    module.params['commit_files'],
                   )

    state = module.params['state']

    if state == 'present':
        results = git.commit()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        if results.has_key('no_commits'):
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
