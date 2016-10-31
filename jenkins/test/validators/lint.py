''' Run pylint against each python file with changes '''

import os
import re
import sys
import common

PYLINT_RCFILE = "jenkins/test/validators/.pylintrc"
LINT_EXCLUDE_PATTERN_LIST = [
    r'prometheus_client'
    r'ansible/inventory/aws/hosts/ec2.py'
    r'ansible/inventory/gce/hosts/gce.py'
    r'docs/*']

def linter(base_sha, remote_sha):
    '''Use pylint to lint all python files changed in the pull request'''
    _, diff_output = common.run_cli_cmd(["/usr/bin/git", "diff", "--name-only", base_sha,
                                         remote_sha, "--diff-filter=ACM"])
    diff_file_list = diff_output.split('\n')
    file_list = []

    # For each file in the diff, confirm it should be linted
    for dfile in diff_file_list:
        # Skip linting for specific files
        skip = False
        for exclude_pattern in LINT_EXCLUDE_PATTERN_LIST:
            if re.match(exclude_pattern, dfile):
                skip = True
                break
        if skip:
            continue
        # Skip linting if dfile is a directory or other non-file type
        if not os.path.isfile(dfile):
            continue
        # Skip linting if the file does not have a python extension
        _, ext = os.path.splitext(dfile)
        if ext != ".py":
            continue
        file_list.append(dfile)

    if len(file_list) == 0:
        print "No python files have changed, skipping running python linter"
        return True, ""

    print "Running pylint against " + " ".join(file_list)
    success, stdout = common.run_cli_cmd(["/usr/bin/pylint", "--rcfile=" + PYLINT_RCFILE] + file_list,
                                         exit_on_fail=False)
    if not success:
        return False, "Pylint failed:\n" + stdout
    return True, ""

def usage():
    ''' Print usage '''
    print """usage: python lint.py [[base_sha] [remote_sha]]
    
    base_sha:   The SHA of the current base branch being merged into
    remote_sha: The SHA of the remote branch being merged
    
Arguments can be provided through the following environment variables:

    base_sha:   PRV_BASE_SHA
    remote_sha: PRV_REMOTE_SHA"""

def main():
    ''' Get base and remote SHA from arguments and run linter '''
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
        print "base and remote sha must be defined"
        usage()
        sys.exit(3)
    success, error_message = linter(base_sha, remote_sha)
    if not success:
        print "Pylint failed:"
        print error_message
        sys.exit(1)
    print "Pylint succeeded!"


if __name__ == '__main__':
    main()
