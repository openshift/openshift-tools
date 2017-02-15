""" Run all tests for openshift-tools repository """
# This script expects a single environment variable to be defined:
#    PULL_REQUEST - JSON represntation of the pull request to be tested
#
# The data expected in PULL_REQUEST is defined in the github api here:
#    https://developer.github.com/v3/pulls/#get-a-single-pull-request
# The same data is provided in the webhook, which is defined here:
#    https://developer.github.com/v3/activity/events/types/#pullrequestevent
#
# The script will parse the provided pull request JSON and define a list of environment variables for
# consumption by the validation scripts. Then, each *.py file in ./validators/ (minus specified exclusions)
# will be run. The list of variables defined is below:
#  Github stuff
#    PRV_PULL_ID       ID of the pull request
#    PRV_PULL_URL      URL of the pull request
#
#  Base info
#    PRV_BASE_SHA      SHA of the target being merged into
#    PRV_BASE_REF      ref (usually branch name) of the base
#    PRV_BASE_LABEL    Base label
#    PRV_BASE_NAME     Full name of the base 'namespace/reponame'
#
#  Remote (or "head") info
#    PRV_REMOTE_SHA    SHA of the branch being merged
#    PRV_REMOTE_REF    ref (usually branch name) of the remote
#    PRV_REMOTE_LABEL  Remote label
#    PRV_REMOTE_NAME   Full name of the remote 'namespace/reponame'
#    PRV_CURRENT_SHA   The SHA of the merge commit
#
#  Other info
#    PRV_CHANGED_FILES List of files changed in the pull request
#    PRV_COMMITS       List of commits in the pull request
#

# TODO:
# - Handle failures better. Just exiting is not a good option, as it will likely leave the PR
#    commit status in pending forever. We might be able to better handle this in the webhook now

import os
import json
import subprocess
import sys
import fnmatch

import github_helpers

EXCLUDES = [
    "common.py",
    ".pylintrc"
]

# The path set up in the Dockerfile
WORK_DIR = "/validator/"
# The absolute path to openshift-tools repo
OPENSHIFT_TOOLS_PATH = WORK_DIR + "openshift-tools/"
# The absolute path to the testing validator scripts
VALIDATOR_PATH = OPENSHIFT_TOOLS_PATH + "jenkins/test/validators/"
# Script location of unit tests
UNIT_TEST_SCRIPT = OPENSHIFT_TOOLS_PATH + "jenkins/test/run_unit_tests.sh"
# The absolute path to the ops-rpm repo
OPS_RPM_PATH = WORK_DIR + "ops-rpm/"

# The string to accept in PR comments to initiate testing by a whitelisted user
TEST_STRING = "[test]"

def run_cli_cmd(cmd, exit_on_fail=True, log_cmd=True):
    '''Run a command and return its output'''
    # Don't log the command if log_cmd=False to avoid exposing secrets in commands
    if log_cmd:
        print "> " + " ".join(cmd)
    proc = subprocess.Popen(cmd, bufsize=-1, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                            shell=False)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        # Don't log the command if log_cmd=False to avoid exposing secrets in commands
        if log_cmd:
            print "Unable to run " + " ".join(cmd) + " due to error: " + stderr
        else:
            print "Error running system command: " + stderr
        if exit_on_fail:
            sys.exit(proc.returncode)
        else:
            return False, stdout
    else:
        return True, stdout

def assign_env(pull_request):
    '''Assign environment variables based on pull_request json data and other env variables'''
    # Github environment variables
    # Note that the PR title and body are not set or included in the pull_request json
    # This is to avoid issues with unexpected characters being passed through the jenkins plugin,
    # to openshift, and through json parsing. There are too many unknowns for it to be predictable.
    os.environ["PRV_PULL_ID"] = pull_request["number"]
    os.environ["PRV_URL"] = pull_request["url"]

    # Base environment variables
    base = pull_request["base"]
    os.environ["PRV_BASE_SHA"] = base["sha"]
    os.environ["PRV_BASE_REF"] = base["ref"]
    os.environ["PRV_BASE_LABEL"] = base["label"]
    os.environ["PRV_BASE_NAME"] = base["repo"]["full_name"]

    # Remote environment variables
    head = pull_request["head"]
    os.environ["PRV_REMOTE_SHA"] = head["sha"]
    os.environ["PRV_REMOTE_REF"] = head["ref"]
    os.environ["PRV_REMOTE_LABEL"] = head["label"]
    os.environ["PRV_REMOTE_NAME"] = head["repo"]["full_name"]

    # Other helpful environment variables
    baserepo = base["repo"]["full_name"]
    prnum = pull_request["number"]

    # List of changed files
    changed_files = github_helpers.get_changed_files(baserepo, prnum)
    os.environ["PRV_CHANGED_FILES"] = ",".join(changed_files)

    # List of commits
    commits = github_helpers.get_commits(baserepo, prnum)
    os.environ["PRV_COMMITS"] = ",".join(commits)

def merge_changes(pull_request):
    """ Merge changes into current repository """
    pull_id = pull_request["number"]

    run_cli_cmd(['/usr/bin/git', 'fetch', "--tags", "origin", "+refs/head/*:refs/remotes/origin/*",
                 "+refs/pull/*:refs/remotes/origin/pr/*"])
    _, output = run_cli_cmd(['/usr/bin/git', 'rev-parse',
                             'refs/remotes/origin/pr/'+pull_id+'/merge^{commit}'])
    current_rev = output.rstrip()
    run_cli_cmd(['/usr/bin/git', 'config', 'core.sparsecheckout'], exit_on_fail=False)
    run_cli_cmd(['/usr/bin/git', 'checkout', '-f', current_rev])
    os.environ["PRV_CURRENT_SHA"] = current_rev

def run_validators():
    """ Run all test validators """
    # First, add the validator direcotry to the python path to allow
    # modules to be loaded by pylint
    # We also add the jenkins/test directory so that github_helpers can be properly loaded.
    pypath = os.getenv("PYTHONPATH", "")
    tools_test_path = OPENSHIFT_TOOLS_PATH + "jenkins/test/"
    if pypath != "":
        os.environ["PYTHONPATH"] = VALIDATOR_PATH + os.pathsep + tools_test_path + os.pathsep + pypath
    else:
        os.environ["PYTHONPATH"] = VALIDATOR_PATH + os.pathsep + tools_test_path

    failure_occured = False
    validators = [validator for validator in os.listdir(VALIDATOR_PATH) if
                  os.path.isfile(os.path.join(VALIDATOR_PATH, validator))]
    for validator in validators:
        skip = False
        for exclude in EXCLUDES:
            if validator == exclude:
                skip = True
        if skip:
            continue
        validator_abs = os.path.join(VALIDATOR_PATH, validator)
        executer = ""
        _, ext = os.path.splitext(validator)
        if ext == ".py":
            executer = "/usr/bin/python"
        elif ext == ".sh":
            executer = "/bin/sh"
        # If the ext is not recongized, try to just run the file
        print "Executing validator: " + executer + " " + validator_abs
        success, output = run_cli_cmd([executer, validator_abs], exit_on_fail=False)
        print output
        if not success:
            print validator + " failed!"
            failure_occured = True

    if failure_occured:
        return False
    return True

# Check both the user and org whitelist for the user in this pull request
def pre_test_check(pull_request):
    """ Get and check the user whitelist for testing from mounted secret volume """
    # Get user from pull request
    user = ""
    if "user" in pull_request:
        user = pull_request["user"]["login"]
    else:
        print "Pull request data does not include pull request user or issue comment user data"
        sys.exit(1)

    # Get secret information from env variable
    secret_dir = os.getenv("WHITELIST_SECRET_DIR")
    if secret_dir == "":
        print "ERROR: $WHITELIST_SECRET_DIR undefined. This variable should exist and" + \
            " should point to the mounted volume containing the admin whitelist"
        sys.exit(2)

    # Extract whitelist from secret volume
    user_whitelist_file = open(os.path.join("/", secret_dir, "users"), "r")
    user_whitelist = user_whitelist_file.read()
    user_whitelist_file.close()
    if user_whitelist == "" or user not in user_whitelist.split(","):
        if not check_org_whitelist(user, secret_dir):
            print "WARN: User " + user + " not in admin or org whitelist."
            # exit success here so that the jenkins job is marked as a success,
            # since no actual error occured, the expected has happened
            sys.exit(0)

# Get the members of each organization in the organization whitelist for the user. If
# the user is a member of any of these organizations, return True
def check_org_whitelist(user, secret_dir):
    """ Determine whether user is a member of any org in the org whitelist """
    org_whitelist_file = open(os.path.join("/", secret_dir, "orgs"), "r")
    org_whitelist = org_whitelist_file.read()
    org_whitelist_file.close()
    for org in org_whitelist.split(","):
        if github_helpers.org_includes(user, org):
            return True
    return False

def build_test_tools_rpms():
    """ Build and install the openshift-tools rpms """
    # We only need to build the openshift-tools rpms:
    #   openshift-tools/scripts/openshift-tools-scripts.spec
    #   openshift-tools/ansible/openshift-tools-ansible.spec
    #   openshift-tools/openshift_tools/python-openshift-tools.spec
    #   openshift-tools/web/openshift-tools-web.spec

    # To build them: cd /validator/ops-rpm; /bin/sh /validator/ops-rpm/ops-rpm test-build-git openshift-tools
    # This will unfortunately create a /tmp/titobuild.[A-Za-z0-9]{10} directory for each rpm
    print "Building openshift-tools test rpms..."
    cwd = os.getcwd()

    # Clone the ops-rpm repo
    # The ops-rpm repo is private and requires authentication
    username, token = github_helpers.get_github_credentials()
    opsrpm_url = "https://" + username + ":" + token + "@github.com/openshift/ops-rpm"
    clone_opsrpm_cmd = ["/usr/bin/git", "clone", opsrpm_url, OPS_RPM_PATH]
    success, output = run_cli_cmd(clone_opsrpm_cmd, False, False)
    if not success:
        print "Unable to clone the ops-rpm repo, builds cannot continue: " + output
        sys.exit(1)

    # Change to the ops-rpm directory
    cd_cmd = ["cd", OPS_RPM_PATH]
    success, output = run_cli_cmd(cd_cmd, False)
    if not success:
        print "Unable to change to the ops-rpm directory: " + output
        sys.exit(1)

    # Do the build
    build_cmd = ["/bin/sh", os.path.join(OPS_RPM_PATH, "ops-rpm"), "test-build-git", "openshift-tools"]
    success, output = run_cli_cmd(build_cmd, False)
    if not success:
        print "Unable to build test rpms: " + output
        sys.exit(1)
    else:
        print "Successfully built openshift-tools test rpms!"

    # Change back to previous directory
    cd_cmd = ["cd", cwd]
    # We don't really care if this fails, most things we do are from an absolute path
    run_cli_cmd(cd_cmd, False)

    # The directories ops-rpm creates look like this:
    #   /tmp/titobuild.CzQ1l4W8LM:
    #     noarch
    #     openshift-tools-ansible-0.0.35-1.git.2.74afd1e.el7.centos.src.rpm
    #     openshift-tools-ansible-git-2.aa60bc1.tar.gz
    #   /tmp/titobuild.CzQ1l4W8LM/noarch:
    #     openshift-tools-ansible-filter-plugins-0.0.35-1.git.2.74afd1e.el7.centos.noarch.rpm
    #     openshift-tools-ansible-inventory-0.0.35-1.git.2.74afd1e.el7.centos.noarch.rpm
    #     openshift-tools-ansible-inventory-aws-0.0.35-1.git.2.74afd1e.el7.centos.noarch.rpm
    #     openshift-tools-ansible-inventory-gce-0.0.35-1.git.2.74afd1e.el7.centos.noarch.rpm
    #     openshift-tools-ansible-zabbix-0.0.35-1.git.2.74afd1e.el7.centos.noarch.rpm
    # We want to install all of the *.noarch.rpm files in the tree.
    rpms = []
    for root, _, files in os.walk('/tmp/'):
        # This really assumes that no other *.noarch.rpm files are in /tmp/, we might want to narrow it down
        for filename in files:
            if fnmatch.fnmatch(filename, "*.noarch.rpm"):
                file_abs = os.path.abspath(os.path.join(root, filename))
                rpms.append(file_abs)

    # If we didn't find any rpms, then there must have been some problems building.
    if len(rpms) == 0:
        print "No rpms found in /tmp/ after test build of openshift-tools"
        sys.exit(1)

    # Install the rpms, in one big yum install command
    yum_install_cmd = ["yum", "localinstall", " ".join(rpms)]
    success, output = run_cli_cmd(yum_install_cmd, False)
    return success, output

def run_unit_tests():
    """ Run unit tests against installed tools rpms """
    # At the time of this writing, no unit tests exist.
    # A unit tests script will be run so that unit tests can easily be modified
    print "Running unit tests..."
    success, output = run_cli_cmd(["/bin/sh", UNIT_TEST_SCRIPT], False)
    return success, output

def main():
    """ Get the pull request data, merge changes, assign env, and run validators """
    # Get the pull request json from the defined env variable
    pull_request_json = os.getenv("PULL_REQUEST", "")
    if pull_request_json == "":
        print 'No JSON data provided in $PULL_REQUEST environment variable'
        sys.exit(1)
    try:
        pull_request = json.loads(pull_request_json, parse_int=str, parse_float=str)
    except ValueError as error:
        print "Unable to load JSON data from $PULL_REQUEST environment variable:"
        print error
        sys.exit(1)

    # Run several checks to ensure tests should be run for this pull request
    pre_test_check(pull_request)

    # These variables will be used at the end of testing to submit status updates
    remote_sha = pull_request["head"]["sha"]
    pull_id = pull_request["number"]
    repo = pull_request["base"]["repo"]["full_name"]

    # Merge changes from pull request
    merge_changes(pull_request)

    # Assign env variables for validators
    assign_env(pull_request)

    # Run validators
    validators_success = run_validators()

    # Determine and post result of tests
    if not validators_success:
        github_helpers.submit_pr_comment("Validation tests failed!", pull_id, repo)
        github_helpers.submit_pr_status_update("failure", "Validation tests failed",
                                               remote_sha, repo)
        sys.exit(1)

    print "Validation tests passed!"
    # Build test rpms
    build_success, output = build_test_tools_rpms()
    if not build_success:
        print "Rpm test builds failed, output:"
        print output
        github_helpers.submit_pr_comment("Validation tests passed, rpm test builds failed!", pull_id, repo)
        github_helpers.submit_pr_status_update("failure", "Validation tests passed, rpm test builds failed",
                                               remote_sha, repo)
        sys.exit(1)

    print "Test rpms built!"
    # Run unit tests
    unittest_success, output = run_unit_tests()
    if not unittest_success:
        print "Unit tests failed, output:"
        print output
        github_helpers.submit_pr_comment("Validation tests passed, test rpms built, unit tests failed!", pull_id, repo)
        github_helpers.submit_pr_status_update("failure", "Validation tests passed, test rpms built, unit tests failed",
                                               remote_sha, repo)
        sys.exit(1)

    print "Unit tests passed!"
    # If we are here, then everything succeeded!
    github_helpers.submit_pr_comment("All tests passed!", pull_id, repo)
    github_helpers.submit_pr_status_update("success", "All tests passed",
                                           remote_sha, repo)

if __name__ == '__main__':
    main()
