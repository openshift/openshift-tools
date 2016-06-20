# pylint: skip-file

class GitStatus(GitCLI):
    ''' Class to wrap the git merge line tools
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path):
        ''' Constructor for GitStatus '''
        super(GitStatus, self).__init__(path)
        self.path = path
        self.debug = []

        os.chdir(path)

    def status(self):
        '''perform a git status '''

        return self._status(uno=True)
