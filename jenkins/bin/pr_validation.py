#!/usr/bin/env python

"""
Validate a pull request for openshift-tools
"""

import sys
import subprocess
import os
import re
import requests
import yaml_validation

GITHUB_API_URL = "https://api.github.com/"
REPO = "tiwillia/openshift-tools"
PULL_ID_ENVVAR = "TOOLS_PULL_ID"
PROD_BRANCH_NAME = "prod"
PYLINT_RCFILE = "jenkins/.pylintrc"
LINT_EXCLUDE_PATTERN_LIST = [
    r'prometheus_client'
    r'ansible/inventory/aws/hosts/ec2.py'
    r'ansible/inventory/gce/hosts/gce.py'
    r'docs/*']

# Mostly stolen from parent.py
# Run cli command. By default, exit when an error occurs
def run_cli_cmd(cmd, exit_on_fail=True):
    '''Run a command and return its output'''
    proc = subprocess.Popen(cmd, bufsize=-1, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        if exit_on_fail:
            print stdout
            print "Unable to run " + " ".join(cmd) + " due to error: " + stderr
            sys.exit(proc.returncode)
        else:
            return False, stdout
    else:
        return True, stdout

# Run pylint against python files with changes
def linter(base_sha, remote_sha):
    '''Use pylint to lint all python files changed in the pull request'''
    _, diff_output = run_cli_cmd(["/usr/bin/git", "diff", "--name-only", base_sha, remote_sha, "--diff-filter=ACM"])
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
        # Skip linting if the file is documentation
        _, ext = os.path.splitext(dfile)
        if ext == "adoc" or ext == "asciidoc":
            continue
        # Finally, if this file is indeed a python script, add it to the list to be linted
        _, file_type = run_cli_cmd(["/usr/bin/file", "-b", dfile])
        if re.match(r'python', file_type, flags=re.IGNORECASE):
            file_list.append(dfile)

    if len(file_list) == 0:
        print "No python files have changed, skipping running python linter"
        return

    print "Running pylint against " + " ".join(file_list)
    success, stdout = run_cli_cmd(["/usr/bin/pylint", "--rcfile=" + PYLINT_RCFILE] + file_list, exit_on_fail=False)
    if not success:
        return False, "Pylint failed:\n" + stdout
    return True, ""

def validate_yaml(base_sha, remote_sha):
    '''Validate all yaml files to ensure proper format'''
    print "Validating yaml"
    sys.argv = [sys.argv[0], base_sha, remote_sha, ""]

    # TODO This is a bit ugly, it will exit if an error is found, which doesn't give us much of an oppurtunity
    # to handle errors completely in the script
    yaml_validation.main()

def ensure_stg_contains(commit_id):
    '''Ensure that the stg branch contains a specific commit'''
    print "Ensuring stage branch also contains " + commit_id
    # git co stg
    run_cli_cmd(['/usr/bin/git', 'checkout', 'stg'])
    # git pull latest
    run_cli_cmd(['/usr/bin/git', 'pull'])
    # setup on the <prod> branch in git
    run_cli_cmd(['/usr/bin/git', 'checkout', 'prod'])
    run_cli_cmd(['/usr/bin/git', 'pull'])
    # merge the passed in commit into my current <branch>
    run_cli_cmd(['/usr/bin/git', 'merge', commit_id])

    commits_not_in_stg = []

    # get the differences from stg and <branch>
    _, rev_list = run_cli_cmd(['/usr/bin/git', 'rev-list', '--left-right', 'stg...prod'])
    for commit in rev_list.split('\n'):
        # continue if it is already in stg
        if not commit or commit.startswith('<'):
            continue
        # remove the first char '>'
        commit = commit[1:]
        success, branches = run_cli_cmd(['/usr/bin/git', 'branch', '-q', '-r', '--contains', commit],
                                        exit_on_fail=False)
        if success and len(branches) == 0:
            continue
        if 'origin/stg/' not in branches:
            commits_not_in_stg.append(commit)

    if len(commits_not_in_stg) > 0:
        return False, "These commits are not in stage:\n\t" + " ".join(commits_not_in_stg)
    return True, ""

def main():
    '''Get pull request information from github and run validation'''
    if not re.match(r'.*\/openshift-tools', os.getcwd()):
        print "ERROR: Script must be run in openshift-tools git repository"

    error_list = []

    # Get the pull ID from environment variable
    pull_id = os.getenv(PULL_ID_ENVVAR, "")
    if pull_id == "":
        # Exit with an error if no pull ID could be found
        print "ERROR: " + PULL_ID_ENVVAR + " is not defined in env"
        sys.exit(1)

    pull_url = GITHUB_API_URL + "repos/" + REPO + "/pulls/" + pull_id
    print "Validating pull request: " + pull_url
    # Attempt to get the pull request
    response = requests.get(pull_url)
    # Raise an error if we get a non-2XX status code back
    response.raise_for_status()

    pull_content = response.json()
    base_ref = pull_content["base"]["ref"]
    # This is the same as $COMMIT_ID in previous jenkins workflow
    base_sha = pull_content["base"]["sha"]
    #base_url = pull_content["base"]["repo"]["git_url"]
    remote_ref = pull_content["head"]["ref"]
    remote_sha = pull_content["head"]["sha"]
    remote_url = pull_content["head"]["repo"]["git_url"]
    test_branch_name = "tpr-" + remote_ref + "_" + pull_content['user']['login']

    run_cli_cmd(['/usr/bin/git', 'checkout', '-b', test_branch_name])
    run_cli_cmd(['/usr/bin/git', 'pull', remote_url, remote_ref])
    run_cli_cmd(['/usr/bin/git', 'pull', remote_url, remote_ref, '--tags'])
    run_cli_cmd(['/usr/bin/git', 'checkout', base_ref])
    run_cli_cmd(['/usr/bin/git', 'merge', test_branch_name])

    # Run yaml validation on any yaml files
    # TODO currently validate_yaml exits when a failure is found, I'd rather it return an error message
    validate_yaml(base_sha, remote_sha)
    # Run the python linter on any changed python files
    success, error_message = linter(base_sha, remote_sha)
    if not success:
        error_list.append(error_message)
    # If this pull request is submitting to prod, ensure the stage branch already contains this commit
    if base_ref == PROD_BRANCH_NAME:
        success, error_message = ensure_stg_contains(remote_sha)
        if not success:
            error_list.append(error_message)

    if len(error_list) > 0:
        for error_message in error_list:
            print "ERROR: " + error_message
        sys.exit(1)
    print "SUCCESS!"

if __name__ == '__main__':
    main()
