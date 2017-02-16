# pylint: skip-file

class GitFetch(GitCLI):
    ''' Class to wrap the git merge line tools '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 path,
                 remote,
                 ssh_key=None):
        ''' Constructor for GitFetch '''
        super(GitFetch, self).__init__(path, remote, ssh_key=ssh_key)
        self.remote = remote
        self.debug = []

        if not os.path.isdir(self.path):
            print "Git checkout directory does not exist. Exiting..."
            sys.exit(1)

    def fetch(self):
        ''' fetch from the selected remote '''

        os.chdir(self.path)

        fetch_results = self._fetch(self.remote)
        no_fetch_needed = False

        # TODO: Check for no results
        if fetch_results['returncode'] != 0:
            return {'returncode': 1,
                    'results': fetch_results,
                    'error_msg': 'Unable to fetch for remote: ' + self.remote,
                    'no_fetch_needed': False
                   }

        # git fetch returns output to stderr.
        # Success but no stderr contents implies nothing was fetched.
        no_fetch_needed = len(fetch_results['stderr']) == 0
        return {'returncode': 0,
                'results': fetch_results,
                'no_fetch_needed': no_fetch_needed
               }

