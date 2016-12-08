temp_dir_git_clone
==================

A simple ansible module that will checkout a git repo to a temp
directory. It will set a fact called tdgc_retval_repo_dir with a path to
the cloned repository.

Requirements
------------
None

Role Variables
--------------
- tdgc_repo_name: name of the repository, used for the directory to checkout into
- tdgc_repo: The git repository. ex: git@github.com:openshift/openshift-ansible.git
- tdgc_branch: The branch to checkout
- tdgc_ssh_key: Variable of the ssh private to to use to do a clone

Dependencies
------------
None

Example Playbook
----------------

    - hosts: localhost
      roles:
         - { role: temp_dir_git_clone, tdgc_repo_name: openshift_ansible, tdgc_repo: "git@github.com:openshift/openshift-ansible" }
      tasks:
         - debug: var=tdgc_retval_repo_dir

License
-------
Copyright 2015 Red Hat Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author Information
------------------
Openshift Operations, Red Hat, Inc.
