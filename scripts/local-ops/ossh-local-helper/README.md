# osops-noc-ossh-local-helper
A helper to make parts of ossh work locally

# Usage
* `ossh hos<tab><tab>`: autocomplete possible hosts
* `ossh hostname`: ssh to that host via bastion
* `ossh hostname mon`: ssh to that host via bastion and connect to monitoring container

# Installation
* git clone to your local disk
* add to bashrc:
```
# ~/.bashrc OSSH helper, /path/to/project means where you put git/openshift-tools/scripts/local-ops/ossh-local-helper
export OSSH_HELPER_BASEDIR=/path/to/project

# setup your remote host(jumphost) user, usually it's your kerberos username
export myUser=$kerberos_name

# setup the jumphost
export bastion="bastion.ops.example.com"

# -v is optional
# --target-host is intentionally blank as it will take the very next argument as target-host
alias ossh="${OSSH_HELPER_BASEDIR}/ossh.py3 -v --bastion-user $myUser --bastion-host $bastion --target-user root --target-host'

# required for OSSH_HELPER_CACHE
source ${OSSH_HELPER_BASEDIR}/ossh.bashrc
export OSSH_HELPER_BASTION=$bastion
export OSSH_HELPER_CACHE=${OSSH_HELPER_BASEDIR}/ossh-list.bash
```
