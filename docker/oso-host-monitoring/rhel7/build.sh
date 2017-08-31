#!/bin/bash
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 


# Make sure the script exits on first error
set -e

RED="$(echo -e '\033[1;31m')"
NORM="$(echo -e '\033[0m')"

function handle_err() {
  echo -e "\n${RED}ERROR: build script failed.${NORM}\n"
}

trap handle_err ERR

function handle_cleanup() {
  echo -n "Removing the fingerprint... "
  [ -f ${container_fingerprint} ] && rm -f "${container_fingerprint}"
  echo "Done."
}

trap handle_cleanup  INT TERM EXIT

sudo echo -e "\nTesting sudo works...\n"

# We MUST be in the same directory as this script for the build to work properly
cd $(dirname $0)

# generate container fingerprint (user/location/timestamp/git information)
container_fingerprint='./container-build-env-fingerprint.output'
./container-build-env-fingerprint.sh > ${container_fingerprint}

# Build ourselves
echo
echo "Building oso-rhel7-host-monitoring..."
sudo time docker build $@ -t oso-rhel7-host-monitoring .
