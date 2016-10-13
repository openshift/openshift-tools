# pylint: skip-file

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
