#!/bin/bash

# TODO
# Handle failure scenarios

GIT_COMMIT=$1
# The below were previously extracted using the jenkins pull request builder plugin
ghprbTargetBranch=$2
ghprbActualCommit=$3

echo $(pwd)
./yaml_validation.sh "$(/usr/bin/git rev-parse HEAD^)" "$GIT_COMMIT" "$ghprbTargetBranch"
./pylint.sh $(/usr/bin/git rev-parse HEAD^) $GIT_COMMIT $ghprbTargetBranch
./parent.py $ghprbTargetBranch $ghprbActualCommit
