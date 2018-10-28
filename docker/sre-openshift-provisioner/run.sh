#!/bin/bash -e

# setting up AWS STS Token
SRE_AWS_STS_JSON=$(aws sts get-session-token)
AWS_ACCESS_KEY_ID=$(echo ${SRE_AWS_STS_JSON} | jq -r '.Credentials.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo ${SRE_AWS_STS_JSON} | jq -r '.Credentials.SecretAccessKey')
AWS_SESSION_TOKEN=$(echo ${SRE_AWS_STS_JSON} | jq -r '.Credentials.SessionToken')

echo -n "Running sre-openshift-provisioner... "

# TODO: Remove privileged, net=host and OO_PAUSE_ON_START
sudo docker run --rm=true -it --name sre-openshift-provisioner    \
             --privileged \
            -e SSH_AUTH_SOCK=${SSH_AUTH_SOCK}       \
            -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
            -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
            -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
            -v $(dirname ${SSH_AUTH_SOCK}):$(dirname ${SSH_AUTH_SOCK})    \
            -v /tmp/${USER}/${CLUSTERID}_inventory.yml:/tmp/inventory.yml \
            sre-openshift-provisioner bash $@

echo "Done."
