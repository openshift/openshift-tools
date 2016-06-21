# pylint: skip-file

class GitDiff(GitCLI):
    ''' Class to wrap the git merge line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 branch,
                 diff_branch,
                ):
        ''' Constructor for GitStatus '''
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
        '''perform a git status '''

        if self.checkout_branch():
            diff_results = self._diff(self.diff_branch)
            return diff_results
