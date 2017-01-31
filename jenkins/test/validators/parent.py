''' Ensure any changes to prod branch also exist in stg '''
import os
import sys
import common

PROD_BRANCH_NAME = "prod"
STG_BRANCH_NAME = "stg"

# Takes an array of commit SHA strings
def ensure_stg_contains(commit_shas):
    '''Ensure that the stg branch contains a specific commit'''
    print "Ensuring stage branch also contains " + ",".join(commit_shas)

    commits_not_in_stg = []
    for commit in commit_shas:
        parent_cmd = ['/usr/bin/git', 'branch', '-q', '-r', '--contains', commit]
        success, branches = common.run_cli_cmd(parent_cmd, exit_on_fail=False)
        if not success or len(branches) != 0:
            if 'origin/stg' not in branches:
                # If not, this commit is not in stg and should not be merged to prod
                commits_not_in_stg.append(commit)

    if len(commits_not_in_stg) > 0:
        return False, "These commits are not in stage:\n\t" + " ".join(commits_not_in_stg)
    return True, ""

def usage():
    ''' Print usage '''
    print """usage: parent.py base_branch commit_list

    base_branch:  Branch commits are being merged into.
    commit_list:  Comma-seperated list of commits to check for in {}

Arguments can be provided through the following environment variables:

    base_branch:  PRV_BASE_REF
    commit_list:  PRV_COMMITS""".format(PROD_BRANCH_NAME)

def main():
    ''' Get git change information and check stg for commit '''
    if len(sys.argv) == 3:
        base_branch = sys.argv[1]
        commit_list = sys.argv[2]
    elif len(sys.argv) > 3:
        print len(sys.argv)-1, "arguments provided, expected 2."
        usage()
        sys.exit(2)
    else:
        base_branch = os.getenv("PRV_BASE_REF", "")
        commit_list = os.getenv("PRV_COMMITS", "")
    if base_branch == "" or commit_list == "":
        print "Base branch and commit list must be provided"
        usage()
        sys.exit(3)
    if base_branch == PROD_BRANCH_NAME:
        commit_shas = []
        for sha in commit_list.split(","):
            commit_shas.append(sha)
        success, error_message = ensure_stg_contains(commit_shas)
        if not success:
            print error_message
            sys.exit(1)
        print "Parent check succeeeded!"
        sys.exit(0)
    print "Skipping parent check since branch is not", PROD_BRANCH_NAME

if __name__ == '__main__':
    main()
