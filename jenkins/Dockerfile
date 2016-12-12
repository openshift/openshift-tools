FROM centos

# Get EPEL
RUN yum install -y https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm

# Install dependencies
RUN yum install -y git python-pip python pylint python-requests PyYAML file

RUN mkdir /validator && \
    git clone https://github.com/openshift/openshift-tools /validator/openshift-tools && \
    cd /validator/openshift-tools && \
    git checkout stg && \
    git config user.name validator && \
    git config user.email validator@localhost && \
    # Get latest yaml validation script from openshift-ansible repository
    curl https://raw.githubusercontent.com/openshift/openshift-ansible/master/git/yaml_validation.py -o /validator/openshift-tools/jenkins/bin/yaml_validation.py && \
    # Fix permissions so we can write to this directory later on
    chown -R 1001:0 /validator && \
    find /validator -exec chgrp 0 {} \; && \
    find /validator -exec chmod g+rw {} \; && \
    find /validator -type d -exec chmod g+x {} +

COPY bin/* /usr/bin/

WORKDIR /validator/openshift-tools

USER 1001

# Sleep forever, since the commands will be run on the pod through 'oc exec'
ENTRYPOINT /usr/bin/sleep_forever
