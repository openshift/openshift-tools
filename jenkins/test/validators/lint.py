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

def linter(diff_file_list):
    '''Use pylint to lint all python files changed in the pull request'''
    file_list = []

    # For each file in the diff, confirm it should be linted
    for dfile in diff_file_list.split(","):
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
        print "No python files have changed or all files are excluded, skipping running python linter"
        return True, ""

    print "Running pylint against " + " ".join(file_list)
    pylint_cmd = ["/usr/bin/pylint", "--rcfile=" + PYLINT_RCFILE] + file_list
    success, stdout = common.run_cli_cmd(pylint_cmd, exit_on_fail=False)
    if not success:
        return False, "Pylint failed:\n" + stdout
    return True, ""

def usage():
    ''' Print usage '''
    print """usage: python lint.py [file_list...]
    
    file_list:  Comma-seperated list of files to run pylint against
    
Arguments can be provided through the following environment variables:

    file_list:  PRV_CHANGED_FILES"""

def main():
    ''' Get base and remote SHA from arguments and run linter '''
    if len(sys.argv) == 2:
        file_list = sys.argv[1]
    elif len(sys.argv) > 2:
        print len(sys.argv)-1, "arguments provided, expected 1."
        usage()
        sys.exit(2)
    else:
        file_list = os.getenv("PRV_CHANGED_FILES", "")

    if file_list == "":
        print "file list must be provided"
        usage()
        sys.exit(3)
    success, error_message = linter(file_list)
    if not success:
        print "Pylint failed:"
        print error_message
        sys.exit(1)
    print "Pylint succeeded!"


if __name__ == '__main__':
    main()
