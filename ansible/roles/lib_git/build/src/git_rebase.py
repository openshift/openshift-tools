# pylint: skip-file

class GitRebase(GitCLI):
    ''' Class to wrap the git merge line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 branch,
                 rebase_branch):
        ''' Constructor for GitPush '''
        super(GitRebase, self).__init__(path)
        self.path = path
        self.branch = branch
        self.rebase_branch = rebase_branch
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

    def remote_update(self):
        ''' update the git remotes '''

        remote_update_results = self._remote_update()

        self.debug.append(remote_update_results)
        if remote_update_results['returncode'] == 0:
            return True

        return False

    def need_rebase(self):
        ''' checks to see if rebase is needed '''

        git_diff_results = self._diff(self.rebase_branch)
        self.debug.append(git_diff_results)

        if git_diff_results['results']:
            return True

        return False

    def rebase(self):
        '''perform a git push '''

        if self.checkout_branch():
            if self.remote_update():
                if self.need_rebase():
                    rebase_results = self._rebase(self.rebase_branch)
                    rebase_results['debug'] = self.debug

                    return rebase_results
                else:
                    return {'returncode': 0,
                            'results': {},
                            'no_rebase_needed': True
                           }

        return {'returncode': 1,
                'results': {},
                'debug': self.debug
               }
