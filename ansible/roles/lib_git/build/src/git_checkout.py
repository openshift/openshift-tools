# pylint: skip-file

class GitCheckout(GitCLI):
    ''' Class to wrap the git checkout command line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 branch):
        ''' Constructor for GitCheckout '''
        super(GitCheckout, self).__init__(path)
        self.path = path
        self.branch = branch
        self.debug = []

        os.chdir(path)

    def checkout(self):
        '''perform a git checkout '''

        current_branch_results = self._get_current_branch()

        if current_branch_results['results'] == self.branch:
            current_branch_results['checkout_not_needed'] = True

            return current_branch_results

        rval = {}
        rval['branch_results'] = current_branch_results
        checkout_results = self._checkout(self.branch)
        rval['checkout_results'] = checkout_results
        rval['returncode'] = checkout_results['returncode']

        return rval
