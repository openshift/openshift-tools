# pylint: skip-file

class GitClone(GitCLI):
    ''' Class to wrap the git merge line tools '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 dest,
                 repo,
                 branch,
                 bare,
                 ssh_key=None):
        ''' Constructor for GitPush '''
        super(GitClone, self).__init__(dest, ssh_key=ssh_key)
        self.dest = dest
        self.dest_dir = os.path.split(dest)[0]
        self.local_repo_name = os.path.split(dest)[1]
        self.repo = repo
        self.branch = branch
        self.bare = bare
        self.debug = []

        if not os.path.isdir(self.dest_dir):
            print "Destination directory does not exist. Exiting..."
            sys.exit(1)

    def checkout_branch(self):
        ''' check out the desired branch '''

        current_branch_results = self._get_current_branch()
        self.debug.append(current_branch_results)

        if current_branch_results['results'] == self.branch:
            return True

        current_branch_results = self._checkout(self.branch)
        self.debug.append(current_branch_results)

        if current_branch_results['returncode'] == 0:
            return True

        return False

    def clone(self):
        '''perform a git clone '''

        no_clone_needed = False

        # If the git dest dir exists, let's check it out
        if os.path.isdir(self.dest):
            os.chdir(self.dest)
            git_url = self._config("remote.origin.url")
            self.debug.append(git_url)

            if git_url['results'].strip().rstrip('.git') == self.repo.rstrip('.git'):
                no_clone_needed = True
            else:
                return {'returncode': 1,
                        'error_msg': 'repo dir found, but repo url does NOT match. repo url:  ' + self.repo,
                        'results': {},
                        'debug': self.debug
                       }

        # if git dir doesn't exist, let's change the dest_dir parent dir
        else:
            clone_results = self._clone(self.repo, self.dest, self.bare)
            self.debug.append(clone_results)

            if clone_results['returncode'] != 0:
                return {'returncode': 1,
                        'error_msg': "Unable to clone repo: " + self.repo,
                        'results': {},
                        'debug': self.debug
                       }

        if self.branch:
            os.chdir(self.dest)
            if not self.checkout_branch():
                return {'returncode': 1,
                        'error_msg': "Unable to checkout branch: " + self.branch,
                        'results': {},
                        'debug': self.debug
                       }


        return {'returncode': 0,
                'results': {},
                'debug': self.debug,
                'no_clone_needed': no_clone_needed
               }
