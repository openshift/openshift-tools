''' Ensure any changes to prod branch also exist in stg '''
import os
import sys
import common

PROD_BRANCH_NAME = "prod"

def ensure_stg_contains(commit_id):
    '''Ensure that the stg branch contains a specific commit'''
    print "Ensuring stage branch also contains " + commit_id
    # reset any changes other validators might have made
    common.run_cli_cmd(['/usr/bin/git', 'reset', '--hard'])
    # git co stg
    common.run_cli_cmd(['/usr/bin/git', 'checkout', 'stg'])
    # git pull latest
    common.run_cli_cmd(['/usr/bin/git', 'pull'])
    # setup on the <prod> branch in git
    common.run_cli_cmd(['/usr/bin/git', 'checkout', 'prod'])
    common.run_cli_cmd(['/usr/bin/git', 'pull'])
    # merge the passed in commit into my current <branch>
    common.run_cli_cmd(['/usr/bin/git', 'merge', commit_id])

    commits_not_in_stg = []

    # get the differences from stg and <branch>
    _, rev_list = common.run_cli_cmd(['/usr/bin/git', 'rev-list', '--left-right', 'stg...prod'])
    for commit in rev_list.split('\n'):
        # continue if it is already in stg
        if not commit or commit.startswith('<'):
            continue
        # remove the first char '>'
        commit = commit[1:]
        parent_cmd = ['/usr/bin/git', 'branch', '-q', '-r', '--contains', commit]
        success, branches = common.run_cli_cmd(parent_cmd, exit_on_fail=False)
        if success and len(branches) == 0:
            continue
        if 'origin/stg/' not in branches:
            commits_not_in_stg.append(commit)

    if len(commits_not_in_stg) > 0:
        return False, "These commits are not in stage:\n\t" + " ".join(commits_not_in_stg)
    return True, ""

def usage():
    ''' Print usage '''
    print """usage: parent.py [[base_ref] [remote_sha]]

    base_ref:    Git REF of the base branch being merged into
    remote_sha:  The SHA of the remote branch after merge (git rev-parse HEAD)

Arguments can be provided through the following environment variables:

    base_ref:    PRV_BASE_REF
    remote_sha:  PRV_REMOTE_SHA"""

def main():
    ''' Get git change information and check stg for commit '''
    if len(sys.argv) == 3:
        base_ref = sys.argv[1]
        commit_id = sys.argv[2]
    elif len(sys.argv) > 1:
        print len(sys.argv)-1, "arguments provided, expected 2."
        usage()
        sys.exit(2)
    else:
        base_ref = os.getenv("PRV_BASE_REF", "")
        commit_id = os.getenv("PRV_REMOTE_SHA", "")
    if base_ref == "" or commit_id == "":
        print "Base REF and remote SHA must be defined"
        usage()
        sys.exit(3)
    if base_ref == PROD_BRANCH_NAME:
        success, error_message = ensure_stg_contains(commit_id)
        if not success:
            print error_message
            sys.exit(1)
        print "Parent check succeeeded!"
        sys.exit(0)
    print "Skipping parent check since branch is not", PROD_BRANCH_NAME

if __name__ == '__main__':
    main()
