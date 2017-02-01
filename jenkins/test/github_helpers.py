""" Github-related helpers for tests """

import os
import sys
import requests
from github import Github

# The github API base url
GITHUB_API_URL = "https://api.github.com"

def get_github_credentials():
    """ Get credentials from mounted secret volume """
    secret_dir = os.getenv("OPENSHIFT_BOT_SECRET_DIR")
    if secret_dir == "":
        print "ERROR: $OPENSHIFT_BOT_SECRET_DIR undefined. This variable should exist and" + \
            " should point to the mounted volume containing the openshift-ops-bot username" + \
            " and password"
        sys.exit(2)
    username_file = open(os.path.join("/", secret_dir, "username"), 'r')
    token_file = open(os.path.join("/", secret_dir, "token"), 'r')
    username = username_file.read()
    username_file.close()
    token = token_file.read()
    token_file.close()
    return username, token

def conn():
    """ Helper to create a pyGithub object to interface with Github """
    _, token = get_github_credentials()
    return Github(token)

def submit_pr_comment(text, pull_id, repo):
    """ Submit a comment on a pull request or issue in github """
    # TODO this should use pyGithub if possible, but is fine for now
    github_username, oauth_token = get_github_credentials()
    payload = {'body': text}
    comment_url = "{0}/repos/{1}/issues/{2}/comments".format(GITHUB_API_URL, repo, pull_id)
    response = requests.post(comment_url, json=payload, auth=(github_username, oauth_token))
    # Raise an error if the request fails for some reason
    response.raise_for_status()

def submit_pr_status_update(state, text, remote_sha, repo):
    """ Submit a commit status update with a link to the build results """
    # TODO this should use pyGithub if possible, but is fine for now
    target_url = os.getenv("BUILD_URL")
    github_username, oauth_token = get_github_credentials()
    payload = {'state': state,
               'description': text,
               'target_url': target_url,
               'context': "jenkins-ci"}
    status_url = "{0}/repos/{1}/statuses/{2}".format(GITHUB_API_URL, repo, remote_sha)
    response = requests.post(status_url, json=payload, auth=(github_username, oauth_token))
    # Raise an error if the request fails for some reason
    response.raise_for_status()

def org_includes(user, org):
    """ Check if the organization org includes a member user """
    ghc = conn()
    org_members = ghc.get_organization(org).get_members()
    for member in org_members:
        if member.login == user:
            return True
    return False

# Takes a repo in the form 'org/repo-name' and a pr number string or int
def get_changed_files(repo, pr_num):
    """ Get list of modified files for pull request """
    ghc = conn()
    pull = ghc.get_repo(repo).get_pull(int(pr_num))
    filename_list = []
    for prfile in pull.get_files():
        filename = prfile.filename
        filename_list.append(filename)
    return filename_list

# Takes a repo in the form 'org/repo-name' and a pr number string or int
def get_commits(repo, pr_num):
    """ Get list of commits for a pull request """
    ghc = conn()
    pull = ghc.get_repo(repo).get_pull(int(pr_num))
    commit_list = []
    for commit in pull.get_commits():
        commit_sha = commit.sha
        commit_list.append(commit_sha)
    return commit_list
