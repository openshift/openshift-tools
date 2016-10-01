# pylint: skip-file

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
