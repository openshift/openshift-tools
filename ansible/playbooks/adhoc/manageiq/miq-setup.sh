#!/bin/bash

# Make sure we're in the same dir as this script
cd $(dirname $0)

MIQ_RELEASE_TAG=darga-4.1
MIQ_ANS_MODULE_PATH="/tmp/oso-manageiq-${MIQ_RELEASE_TAG}-ans-module"


mkdir -p $MIQ_ANS_MODULE_PATH

pushd $MIQ_ANS_MODULE_PATH &> /dev/null
git clone https://github.com/dkorn/manageiq-ansible-module.git
popd &> /dev/null

ansible-playbook -e "cli_miq_release_tag=$MIQ_RELEASE_TAG" -e "cli_miq_ans_module_path=$MIQ_ANS_MODULE_PATH/manageiq-ansible-module" miq-setup.yml
