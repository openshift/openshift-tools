#!/usr/bin/env bash


OLDREV=$1
NEWREV=$2
TRG_BRANCH=$3

PYTHON=$(which python)

/usr/bin/git diff --name-only $OLDREV $NEWREV --diff-filter=ACM | \
 grep ".py$" | \
 xargs -r -I{} ${PYTHON} -m pylint --rcfile ${WORKSPACE}/jenkins/.pylintrc  {}

exit $?
