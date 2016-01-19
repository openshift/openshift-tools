#!/bin/bash

/usr/bin/wget -q https://raw.githubusercontent.com/openshift/openshift-ansible/master/git/yaml_validation.py -O jenkins/yaml_validation.py

if [ -e jenkins/yaml_validation.py ];
then
  python jenkins/yaml_validation.py "$@"
else
  exit 1
fi

exit $?
