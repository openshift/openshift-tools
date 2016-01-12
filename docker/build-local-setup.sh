#!/bin/bash -e

RED="$(echo -e '\033[1;31m')"
BLUE="$(echo -e '\033[1;34m')"
NORM="$(echo -e '\033[0m')"


cd $(dirname $0)

echo
echo
echo " --------------------"
echo "| ${BLUE}oso-rhel7-ops-base${NORM} |"
echo " --------------------"
./oso-rhel7-ops-base/build.sh $@

echo
echo
echo " ----------------"
echo "| ${BLUE}oso-rhel7-zaio${NORM} |"
echo " ----------------"
./oso-rhel7-zaio/build.sh $@

echo
echo
echo " --------------------"
echo "| ${BLUE}oso-rhel7-zagg-web${NORM} |"
echo " --------------------"
./oso-rhel7-zagg-web/build.sh $@

echo
echo
echo " -----------------------"
echo "| ${BLUE}oso-rhel7-host-monitoring${NORM} |"
echo " -----------------------"
./oso-rhel7-host-monitoring/build.sh $@
