#!/bin/bash

# TODO
# Handle failure scenarios

TOOLS_BRANCH=$1
REMOTE=$2
REMOTE_BRANCH=$3
GIT_COMMIT=$4

pushd $HOME/openshift-tools
git checkout $TOOLS_BRANCH
git fetch origin $TOOLS_BRANCH
git remote add target https://github.com/$REMOTE
git fetch target $REMOTE_BRANCH
git merge target/$REMOTE_BRANCH

# There is no reason for the below script to require 3 inputs, it just throws away the third. But it still requires 3 inputs ¯\_(ツ)_/¯
./yaml_validation.sh "$(/usr/bin/git rev-parse HEAD^)" "$GIT_COMMIT" "bullshit"
./pylint.sh $(/usr/bin/git rev-parse HEAD^) $GIT_COMMIT $TOOLS_BRANCH
./parent.py $TOOLS_BRANCH $GIT_COMMIT
