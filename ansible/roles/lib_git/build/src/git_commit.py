# pylint: skip-file

class GitCommit(GitCLI):
    ''' Class to wrap the git command line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 msg,
                 path):
        ''' Constructor for GitCommit '''
        super(GitCommit, self).__init__(path)
        self.path = path
        self.msg = msg
        os.chdir(path)

    def has_files(self):
        ''' do we have files to commit?'''

        results = self._status(porcelain=True)
        # test the results
        if results['results']:
            return True

        return False


    def commit(self):
        '''perform a git commit '''
        if self.has_files():
            return self._commit(self.msg)

        return {'returncode': 0,
                'results': {},
                'no_files': True
               }
