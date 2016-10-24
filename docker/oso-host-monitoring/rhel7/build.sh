#!/bin/bash
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 


sudo echo -e "\nTesting sudo works...\n"

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)

# generate container fingerprint (user/location/timestamp/git information)
container_fingerprint='./container-build-env-fingerprint.output'
./container-build-env-fingerprint.sh > ${container_fingerprint}

## Make sure base is built with latest changes since we depend on it.
# commenting this out for now because ops-base does a full rebuild everytime
#if ../oso-rhel7-ops-base/build.sh ; then
  # Build ourselves
  echo
  echo "Building oso-rhel7-host-monitoring..."
  sudo time docker build $@ -t oso-rhel7-host-monitoring .
#fi

# cleanup
rm -f ${container_fingerprint}
