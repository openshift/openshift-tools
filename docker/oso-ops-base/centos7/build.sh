#!/bin/bash -e
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 

RED="$(echo -e '\033[1;31m')"
NORM="$(echo -e '\033[0m')"

sudo echo -e "\nTesting sudo works...\n"

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)


# Build ourselves
echo
echo "Building oso-centos7-ops-base..."
sudo time docker build $@ -t oso-centos7-ops-base . && \
sudo docker tag -f oso-centos7-ops-base openshifttools/oso-centos7-ops-base:latest
DOCKER_EXITCODE=$?


# This shouldn't be needed since we're using -e, but apparently -e isn't working as expected.
if [ $DOCKER_EXITCODE -ne 0 ] ; then
  echo -e "\n${RED}ERROR: docker command failed.${NORM}\n"
  exit $DOCKER_EXITCODE
fi
