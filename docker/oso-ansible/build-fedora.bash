#!/bin/bash
set -vx

export baseOS=fedora
export baseOSfrom=fedora:25

source ./function.bash

export ansibleRPM=https://kojipkgs.fedoraproject.org/packages/ansible/2.2.2.0/1.fc25/noarch/ansible-2.2.2.0-1.fc25.noarch.rpm
export ansibleVersion=2.2.2.0-1
export dockerPush=false
buildAnsibleContainer

export ansibleRPM=https://kojipkgs.fedoraproject.org/packages/ansible/2.3.0.0/3.fc25/noarch/ansible-2.3.0.0-3.fc25.noarch.rpm
export ansibleVersion=2.3.0.0-3
export dockerPush=false
buildAnsibleContainer
