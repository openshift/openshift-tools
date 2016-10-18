#!/bin/bash

cat << EOF
BuildUsername: `whoami`
BuildDate: `date`
BuildHostname: `hostname`
BuildFilesystemLocation: `pwd`

git remote -v
`git remote -v`

git log -3:
`git log -3`
EOF

