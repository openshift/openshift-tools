# pylint: skip-file

class GitMerge(GitCLI):
    ''' Class to wrap the git merge line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 merge_id,
                 branch,
                 author=None):
        ''' Constructor for GitCommit '''
        super(GitMerge, self).__init__(path, author=author)
        self.path = path
        self.merge_id = merge_id
        self.branch = branch
        self.author = author
        self.debug = []

        os.chdir(path)

    def checkout_branch(self):
        ''' check out the desired branch '''

        current_branch = self._get_current_branch()

        if current_branch['results'] == self.branch:
            return True

        results = self._checkout(self.branch)
        self.debug.append(results)

        if results['returncode'] == 0:
            return True

        return False

    def merge(self):
        '''perform a git merge '''

        if self.checkout_branch():
            merge_results = self._merge(self.merge_id)
            merge_results['debug'] = self.debug

            if 'Already up-to-date' in merge_results['results']:
                merge_results['no_merge'] = True

            return merge_results

        return {'returncode': 1,
                'results': {},
                'end': 'yes',
                'debug': self.debug
               }
