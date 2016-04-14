#!/usr/bin/env python
'''
  Script to determine if the commits associated with this PR
  have also been merged through the stage branch
'''
#
#  Usage:
#    parent_check.py <branch> <pullrequest_num> <oauth_token>
#
#
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
import subprocess

def run_cli_cmd(cmd, in_stdout=None, in_stderr=None):
    '''Run a command and return its output'''
    if not in_stderr:
        proc = subprocess.Popen(cmd, bufsize=-1, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, shell=False)
    else:
        proc = subprocess.check_output(cmd, bufsize=-1, stdout=in_stdout,
                                       stderr=in_stderr, shell=False)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        return {"rc": proc.returncode, "error": stderr}
    else:
        return {"rc": proc.returncode, "result": stdout}

def main():
    '''Check to ensure that the commits associated with the PR
       that is currently being submitted to prod are also in the stage branch.

       if it is, succeed
       else, fail
    '''
    branch = 'prod'

    if sys.argv[1] != branch:
        sys.exit(0)

    pr_id = sys.argv[2]
    oauth_token = sys.argv[3]

    # git co stg
    if run_cli_cmd(['/usr/bin/git', 'checkout', 'stg'])['rc'] != 0:
        print "\nFAILED: trying to checkout stg"
        sys.exit(100)

    # git pull latest
    if run_cli_cmd(['/usr/bin/git', 'pull'])['rc'] != 0:
        print "\nFAILED: trying to git pull"
        sys.exit(100)

    # get list of commits associated with this PR
    url = "https://api.github.com/repos/openshift/openshift-tools/pulls/{}/commits".format(pr_id)
    response = requests.get(url, auth=HTTPBasicAuth('openshift-ops-bot', oauth_token))
    if response.status_code != 200:
        print "\nFAILED: Problem talking with GitHub API"
        sys.exit(response.status_code)

    commits = json.loads(response.text)

    # check each sha to ensure it's in 'stg'
    not_found_count = 0
    for commit in commits:
        result = run_cli_cmd(['/usr/bin/git', 'branch', '--contains',
                              commit['sha'], '--list', 'stg'])

        if result['rc'] != 0 or 'stg' not in result['result']:
            if not_found_count == 0:
                print "\nFAILED: (These commits from the PR are not in stage.)\n"
            print "\t%s" % commit['sha']
            not_found_count += 1

    sys.exit(not_found_count)

if __name__ == '__main__':
    main()

