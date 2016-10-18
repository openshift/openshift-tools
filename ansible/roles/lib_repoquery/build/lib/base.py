# pylint: skip-file
'''
   class that wraps the repoquery commands in a subprocess
'''
# pylint: disable=too-many-lines

from collections import defaultdict
from distutils.version import LooseVersion
import subprocess

class RepoqueryCLIError(Exception):
    '''Exception class for repoquerycli'''
    pass

# pylint: disable=too-few-public-methods
class RepoqueryCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self,
                 verbose=False):
        ''' Constructor for RepoqueryCLI '''
        self.verbose = verbose
        self.verbose = True

    def _repoquery_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for repoquery '''
        cmds = ['/usr/bin/repoquery', '--quiet']

        cmds.extend(cmd)

        rval = {}
        results = ''
        err = None

        if self.verbose:
            print ' '.join(cmds)

        proc = subprocess.Popen(cmds,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        rval = {"returncode": proc.returncode,
                "results": results,
                "cmd": ' '.join(cmds),
               }

        if proc.returncode == 0:
            if output:
                if output_type == 'raw':
                    rval['results'] = stdout

            if self.verbose:
                print stdout
                print stderr

            if err:
                rval.update({"err": err,
                             "stderr": stderr,
                             "stdout": stdout,
                             "cmd": cmds
                            })

        else:
            rval.update({"stderr": stderr,
                         "stdout": stdout,
                         "results": {},
                        })

        return rval
