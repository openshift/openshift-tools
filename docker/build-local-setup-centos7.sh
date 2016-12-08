#!/bin/bash -e

RED="$(echo -e '\033[1;31m')"
GREEN="$(echo -e '\033[1;32m')"
BLUE="$(echo -e '\033[1;34m')"
NORM="$(echo -e '\033[0m')"


OS=centos7


function fatal_error() {
  ECODE=$?

  if [ $ECODE -ne 0 ]; then
    echo
    echo -n "${RED}ERROR: fatal error on or near line ${1}"

   # print the message if given
   [ -n "$2" ] && echo -n ": $2"

    echo "${NORM}"
    echo
  fi
}

function box_with_color_message() {
  COLOR=$1
  shift
  STR="$@"
  STRLEN=$((${#STR}+2))

  # Top of box
  echo -n ' '
  for i in $(seq $STRLEN); do echo -n '-'; done;
  echo

  # Middle with colored message
  echo "| ${COLOR}${STR}${NORM} |";

  # Bottom of box
  echo -n ' '
  for i in $(seq $STRLEN); do echo -n '-'; done;
  echo
}

function build_image() {
  OS=$1
  shift
  IMAGE=$1
  shift

  echo
  echo
  box_with_color_message "${BLUE}" "${IMAGE} on ${OS}"
  ./${IMAGE}/generate-containers.yml
  ./${IMAGE}/${OS}/build.sh $@
}


# Setup our traps, so that we see errors on exit
trap 'fatal_error ${LINENO}' ERR

# We need to run from the directory where the script is (we use relative paths)
cd $(dirname $0)

sudo echo "Testing sudo works..."

time (
  build_image "${OS}" oso-ops-base $@

  build_image "${OS}" oso-zaio $@

  build_image "${OS}" oso-zagg-web $@

  build_image "${OS}" oso-host-monitoring $@
)
