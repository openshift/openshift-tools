""" Run real rpm builds after new changes are merged """

# Steps used to build rpms are taken from:
#   https://github.com/openshift/ops-sop/blob/master/GitHub/openshift-tools/BuildRpms.asciidoc
# However, there is one major difference. We will not be pushing to the STG and PROD repos.
# Instead, rpms will be pushed to new repositories set up in s3 buckets. There will be a repo for
# stg and a seperate repo for prod. The containers will need to be updated to pull rpms from the new repos.

import sys
import os
import re
import json
import boto3
import ci_util as util
import github_helpers

# RPM                       Directory of RPM source and spec
# -------------------------------------------------------
# openshift-tools-ansible   openshift-tools/ansible
# openshift-tools-web       openshift-tools/web
# openshift-tools-scripts   openshift-tools/scripts
# python-openshift-tools    openshift-tools/openshift_tools
RPM_MAP = {'openshift-tools-ansible': 'ansible',
           'openshift-tools-web': 'web',
           'openshift-tools-scripts': 'scripts',
           'python-openshift-tools': 'openshift_tools'}

# Keep track of the tags and rpms we've pushed, in case a failure occurs we can give accurate
# recovery information
PUSHED_TAGS = []
PUSHED_RPMS = []

# Make sure we know where the openshift-tools directory is
# This is set in the pre_build_setup
OPENSHIFT_TOOLS_DIR = "/builder/openshift-tools"

def pre_build_setup(branch, repo):
    """ Run checks and setup the environment to build rpms """
    # We should first check the branch. If the branch isn't prod/stg/int, we don't need to do anything.
    if branch not in ["prod", "stg", "int"]:
        print "Base branch is not prod, stg, or int. Not building rpms..."
        sys.exit(0)

    # Ensure openshift-tools has already been cloned to this directory
    cwd = os.getcwd()
    cwd_contents = os.listdir(cwd)
    username, token = github_helpers.get_github_credentials()
    if "openshift-tools" not in cwd_contents:
        tools_url = "https://" + username + ":" + token + "@github.com/" + repo
        clone_tools_cmd = ["/usr/bin/git", "clone", tools_url, os.path.join(cwd, "openshift-tools")]
        success, output = util.run_cli_cmd(clone_tools_cmd, False, False)
        if not success:
            print "Unable to clone the openshift-tools repo, builds cannot continue: " + output
            sys.exit(1)

    # Change to the repo directory
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, "openshift-tools"))

    # Update the origin remote url to include authentication to avoid prompts
    push_url = "https://" + username + ":" + token + "@github.com/" + repo
    git_remote_cmd = ["/usr/bin/git", "remote", "set-url", "--push", "origin", push_url]
    success, output = util.run_cli_cmd(git_remote_cmd, False, False)
    if not success:
        print "Unable to set git push remote:"
        print output
        sys.exit(1)

    # Set username and email in git, this is required for pushes
    # TODO really not sure if its ok to be using the noreply email on pushes, but it seems to be fine
    email = "openshift-ops-bot@users.noreply.github.com"
    username_cmd = ["/usr/bin/git", "config", "--global", "user.name", username]
    util.run_cli_cmd(username_cmd)
    email_cmd = ["/usr/bin/git", "config", "--global", "user.email", email]
    util.run_cli_cmd(email_cmd)

    # Checkout the correct branch
    checkout_cmd = ["/usr/bin/git", "checkout", branch]
    util.run_cli_cmd(checkout_cmd)

    # Pull the latest code
    pull_cmd = ["/usr/bin/git", "pull"]
    util.run_cli_cmd(pull_cmd)

    # Fetch tags
    fetch_tags_cmd = ["/usr/bin/git", "fetch", "--tags"]
    success, _ = util.run_cli_cmd(fetch_tags_cmd, False)
    if not success:
        print "Unable to fetch the latest tags for " + repo + " on " + branch

    # Change back to the original working directory
    os.chdir(cwd)

# Currently the following rpms are considered for building when files in a directory are changed:
# RPM                       Directory to look for changes
# -------------------------------------------------------
# openshift-tools-ansible   openshift-tools/ansible
# openshift-tools-web       openshift-tools/web
# openshift-tools-scripts   openshift-tools/scripts
# python-openshift-tools    openshift-tools/openshift_tools
def determine_rpms_with_changes(changed_files):
    """ Determine which openshift-tools rpms have changes made """
    changed_dirs = [filename.split("/")[0] for filename in changed_files]
    rpms_with_changes = []
    for rpm, dir_name in RPM_MAP.iteritems():
        if dir_name in changed_dirs:
            print "Changes found in " + dir_name + " for rpm " + rpm
            rpms_with_changes.append(rpm)
    return rpms_with_changes

def tag_rpms(rpms):
    """ Tag rpms with tito """
    cwd = os.getcwd()
    # Collect all the push commands and only push them after all tags were successful
    push_cmds = {}
    for rpm in rpms:
        print "Tagging rpm " + rpm
        rpm_dir = RPM_MAP[rpm]
        # Change to the repo directory
        os.chdir(os.path.join("openshift-tools", rpm_dir))

        # Tag the rpm
        tag_cmd = ["tito", "tag", "--accept-auto-changelog"]
        success, output = util.run_cli_cmd(tag_cmd, False)
        print output
        if not success:
            print "Unable to tag rpm " + rpm
            print error_msg()
            sys.exit(1)

        # Parse the output for the push command
        for line in output.splitlines():
            if "Push:" in line.split():
                push_cmd = re.split("Push: ", line)[-1]
                push_cmds[rpm] = push_cmd.split(" && ")[-1]
                break

        # Change back to the original working directory
        os.chdir(cwd)

    # Push all of the tags
    for rpm, tag_push_cmd in push_cmds.iteritems():
        # Change to the repo directory
        os.chdir(os.path.join("openshift-tools", rpm_dir))

        tag = tag_push_cmd.split(" ")[-1]
        print "Pushing tag for " + tag

        push_cmd = ["/usr/bin/git", "push", "origin"]
        # TODO
        # Since we aren't ready to push rpms to the s3 repos, we don't want to push tags yet either.
        # Once we are ready, uncomment the following lines to actually push tags:
        #   # util.run_cli_cmd(push_cmd, False)
        #   # success, output = util.run_cli_cmd(tag_push_cmd, False)
        # Then delete the below two lines so we actually test success properly:
        print "Normally would push tag, but not pushing any tags as we do not have an s3 repo set up just yet."
        success = True
        output = ""

        if not success:
            # If this fails after already pushing another tag, the other tag pushes must be
            # manually undone. Hopefully this is the first tag and first failure
            print "FATAL ERROR: Unable to push tag for " + tag + ":"
            print output
            if len(PUSHED_TAGS) > 0:
                print error_msg()

        # If successful, add the tags to the list of pushed tags in case there is a failure
        PUSHED_TAGS.append(tag)

        # Change back to the original working directory
        os.chdir(cwd)

def build_rpms(rpms):
    """ Build and sign rpms """
    # Get the rpm signing key
    secret_dir = os.getenv("RPM_SIGNING_SECRET_DIR")
    if secret_dir == "":
        print "Unable to get rpm signing key, $RPM_SIGNING_SECRET_DIR is undefined"
        print error_msg()
        sys.exit(1)
    rpm_signing_key_file = open(os.path.join("/", secret_dir, "key"))
    rpm_signing_key = rpm_signing_key_file.read()
    if rpm_signing_key == "":
        print "Unable to get rpm signing key, secret key file is empty"
        print error_msg()
        sys.exit(1)
    rpm_signing_key_file.close()

    built_rpms = []
    for rpm in rpms:
        print "Building rpm " + rpm
        # Make temporary directory for rpms
        mktmp_rhel6_cmd = ["mktemp", "-d", "/tmp/titobuild6.XXXXX"]
        mktmp_rhel7_cmd = ["mktemp", "-d", "/tmp/titobuild7.XXXXX"]
        _, tito_dir_6_output = util.run_cli_cmd(mktmp_rhel6_cmd)
        _, tito_dir_7_output = util.run_cli_cmd(mktmp_rhel7_cmd)

        tito_dir_6 = tito_dir_6_output.rstrip()
        tito_dir_7 = tito_dir_7_output.rstrip()

        # Change into the rpm's directory in the openshift-tools repo
        os.chdir(os.path.join("openshift-tools", RPM_MAP[rpm]))

        # Define the build commands
        # TODO
        # Since we aren't ready to push rpms to s3 repos, we don't want to do actual tito builds. Doing the actul build
        # will depend on the new tag being pushed, which isn't happening yet.
        # Instead, we'll use '--test'
        # Another thing we need to look into is whether using the mock builder with the mock configuration is necessary.
        # We believe that it shouldn't be since we are building in an image that we have prepared with all dependencies,
        # which is basically what mock was doing.
        #
        #tito_build_cmd_6 = ["tito", "build", "-o", tito_dir_6, "--builder", "mock", "--arg", "mock=libra6-x86_64",
        #                    "--arg=speedup", "--rpm", "--rpmbuild-options",
        #                    '--define "packager OpenShift Operations" --define "vendor OpenShift Operations"']
        #tito_build_cmd_7 = ["tito", "build", "-o", tito_dir_7, "--builder", "mock", "--arg", "mock=libra7-x86_64",
        #                    "--arg=speedup", "--rpm", "--rpmbuild-options",
        #                    '--define "packager OpenShift Operations" --define "vendor OpenShift Operations"']

        # TODO For now, we are doing test tito builds instead:
        tito_build_cmd_6 = ["tito", "build", "-o", tito_dir_6, "--rpm", "--test", "--rpmbuild-options",
                            '--define "packager OpenShift Operations" --define "vendor OpenShift Operations"']
        tito_build_cmd_7 = ["tito", "build", "-o", tito_dir_6, "--rpm", "--test", "--rpmbuild-options",
                            '--define "packager OpenShift Operations" --define "vendor OpenShift Operations"']

        # Run the builds
        for cmd in [tito_build_cmd_6, tito_build_cmd_7]:
            success, output = util.run_cli_cmd(cmd, False)
            print output
            if not success:
                print "FATAL ERROR: Build of {} failed".format(rpm)
                print error_msg()
                sys.exit(1)

        print "Build of {} succeeded!".format(rpm)

        # Define signing command
        sign_rpms_cmd = ["rpm", "--addsign", "--fskpath=" + rpm_signing_key,
                         os.path.join(tito_dir_6, "*.rpm"), os.path.join(tito_dir_7, "*.rpm")]

        # Sign the builds
        print "Signing {} rpms...".format(rpm)
        success, output = util.run_cli_cmd(sign_rpms_cmd, False, False) # Dont log this command
        if not success:
            print "FATAL ERROR: Unable to sign rpms:"
            print output
        print "Successfully built and signed {}".format(rpm)

        # Get absolute paths to built and signed rpms
        rpm_abs_paths = []
        rpm_abs_paths.append(os.listdir(os.path.join(tito_dir_6, "*.rpm")))
        rpm_abs_paths.append(os.listdir(os.path.join(tito_dir_7, "*.rpm")))

        # Add paths to return array
        built_rpms.append(rpm_abs_paths)

    print "Successfully built all rpms!"
    return built_rpms

# repo can be one of int, stg, or prod
def push_to_repo(repo, rpms):
    """ Push built and signed rpms to the s3 yum repo """
    # TODO
    # rpms should be a list of rpm file paths.
    # Here we will need to get the s3 secret username and access key
    # then we will need to use the s3 sdk to sync up the rpms
    # first, we'll probably need to run createrepo somehow right?
    #   See http://blog.celingest.com/en/2014/09/17/create-your-own-yum-rpm-repository-using-amazon-s3/
    # Use the s3 sdk to upload the updated rpms:
    #   https://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.upload_file

    # Get the s3 secrets location
    s3_secret_dir = os.getenv("S3_ACCESS_SECRET_DIR")
    if s3_secret_dir == "":
        print "Unable to find s3 credentials, $S3_ACCESS_SECRET_DIR is undefined"
        print error_msg()
        sys.exit(1)

    # Get s3 username
    s3_username_file = open(os.path.join("/", s3_secret_dir, "username"))
    s3_username = s3_username_file.read()
    s3_username_file.close()

    # Get s3 acess key
    s3_accesskey_file = open(os.path.join("/", s3_secret_dir, "accesskey"))
    s3_accesskey = s3_accesskey_file.read()
    s3_accesskey_file.close()

    # TODO here we should push the rpms to the yum repos hosted in the s3 buckets
    # For now, we are going to do nothing here. This will ensure that the testing
    print "Would push to {} here, but pushing is not yet implemented".format(repo)

def error_msg():
    """ Generate an error message with instructions on manual recovery """
    if len(PUSHED_TAGS) + len(PUSHED_RPMS) == 0:
        msg = "No changes were made that would require manual recovery."
        return msg
    msg = """
An error has occurred after changes have been made. Manual steps may be required to recover.

The following tags have been pushed and may need to be removed from the upstream openshift-tools repo:\n"""
    for tag in PUSHED_TAGS:
        msg += tag + "\n"
    if len(PUSHED_RPMS) > 0:
        msg += """
The following rpms have been pushed and may need to be reviewed:\n"""
        for rpm in PUSHED_RPMS:
            msg += rpm + "\n"
    return msg

def main():
    """ Build, sign, and push openshift-tools rpms upon a pull request merge """
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

    base_branch = pull_request["base"]["ref"]
    base_repo = pull_request["base"]["repo"]["full_name"]

    # Setup the environment for rpm builds
    pre_build_setup(base_branch, base_repo)

    # Get files with changes from github PR
    prnum = pull_request["number"]
    changed_files = github_helpers.get_changed_files(base_repo, prnum)
    print "Found the following file changes in PR:"
    for filename in changed_files:
        print "  - " + filename

    # Determine the rpms to build based on files changed in PR
    rpms = determine_rpms_with_changes(changed_files)
    if len(rpms) == 0:
        print "No rpm files have been changed, aborting builds..."
        sys.exit(0)

    # Push new tags for rpms about to be built
    tag_rpms(rpms)

    # Build all rpms (we'll only push the ones we tagged though)
    built_rpms = build_rpms(rpms)

    # Push the built rpms to the proper repo
    push_to_repo(base_branch, built_rpms)


if __name__ == '__main__':
    main()
