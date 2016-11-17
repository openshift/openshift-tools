# pylint: skip-file
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
                 verbose=False,
                 ssh_key=None,
                 author=None):
        ''' Constructor for GitCLI '''
        self.path = path
        self.verbose = verbose
        self.ssh_key = ssh_key
        self.author = author
        self.environment_vars = os.environ.copy()

        if self.author:
            author_dict = {}
            author_list = author.split('<')
            author_dict['GIT_COMMITTER_NAME'] = author_list[0].strip()
            author_dict['GIT_COMMITTER_EMAIL'] = author_list[0].strip()

            self.environment_vars.update(author_dict)

    def _add(self, files_to_add=None):
        ''' git add '''

        cmd = ["add", "--no-ignore-removal"]

        if files_to_add:
            cmd.extend(files_to_add)
        else:
            cmd.append('.')

        results = self.git_cmd(cmd)

        return results

    def _commit(self, msg, author=None):
        ''' git commit with message '''

        cmd = ["commit", "-m", msg]

        if author:
            cmd += ["--author", author]

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

        if self.ssh_key:
            with SshAgent() as agent:
                agent.add_key(self.ssh_key)
                proc = subprocess.Popen(cmds,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        env=self.environment_vars)

                stdout, stderr = proc.communicate()

                rval = {"returncode": proc.returncode,
                        "results": results,
                        "cmd": ' '.join(cmds),
                       }
        else:
            proc = subprocess.Popen(cmds,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    env=self.environment_vars)

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
