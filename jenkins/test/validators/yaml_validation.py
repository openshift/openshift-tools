#!/usr/bin/env python
# flake8: noqa
#
#  python yaml validator for a git commit
#
'''
python yaml validator for a git commit
'''
import shutil
import sys
import os
import tempfile
import subprocess
import yaml

def get_changes(oldrev, newrev, tempdir):
    '''Get a list of git changes from oldrev to newrev'''
    proc = subprocess.Popen(['/usr/bin/git', 'diff', '--name-only', oldrev,
                             newrev, '--diff-filter=ACM'], stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    files = stdout.split('\n')

    # No file changes
    if not stdout or stdout == '' or not files:
        return []

    cmd = '/usr/bin/git archive %s %s | /bin/tar x -C %s' % (newrev, " ".join(files), tempdir)
    proc = subprocess.Popen(cmd, shell=True)
    _, _ = proc.communicate()

    rfiles = []
    for dirpath, _, fnames in os.walk(tempdir):
        for fname in fnames:
            rfiles.append(os.path.join(dirpath, fname))

    return rfiles


def usage():
    ''' Print usage '''
    print """usage: yaml_validation.py [[base_sha] [remote_sha]]

    base_sha:    The SHA of the base branch being merged into
    remote_sha:  The SHA of the remote branch being merged

Arguments can be provided through the following environment variables:

    base_sha:    PRV_BASE_SHA
    remote_sha:  PRV_REMOTE_SHA"""

def main():
    '''
    Perform yaml validation
    '''
    if len(sys.argv) == 3:
        base_sha = sys.argv[1]
        remote_sha = sys.argv[2]
    elif len(sys.argv) > 1:
        print len(sys.argv)-1, "arguments provided, expected 2."
        usage()
        sys.exit(2)
    else:
        base_sha = os.getenv("PRV_BASE_SHA", "")
        remote_sha = os.getenv("PRV_REMOTE_SHA", "")
    if base_sha == "" or remote_sha == "":
        print "Base SHA and remote SHA must be defined"
        usage()
        sys.exit(3)

    results = []
    try:
        tmpdir = tempfile.mkdtemp(prefix='jenkins-git-')
        old = base_sha
        new = remote_sha

        for file_mod in get_changes(old, new, tmpdir):

            print "+++++++ Received: %s" % file_mod

            # if the file extensions is not yml or yaml, move along.
            if not file_mod.endswith('.yml') and not file_mod.endswith('.yaml'):
                continue

            # We use symlinks in our repositories, ignore them.
            if os.path.islink(file_mod):
                continue

            try:
                yaml.load(open(file_mod))
                results.append(True)

            except yaml.scanner.ScannerError as yerr:
                print yerr
                results.append(False)
    finally:
        shutil.rmtree(tmpdir)

    if not all(results):
        sys.exit(1)

if __name__ == "__main__":
    main()
