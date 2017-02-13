#!/bin/bash
#set -vx

BASEDIR=`dirname "$(readlink -f "$0")"`
CACHEDIR=${BASEDIR}/cache
CACHEFILE=${CACHEDIR}/${OSSH_HELPER_BASTION}.cache

getIndex() {
    # get data for cache
    ssh -x ${OSSH_HELPER_BASTION} ossh --list \
      | grep -v 'None' \
      | awk '{print $1}' \
      | sort \
      > ${CACHEFILE}
}

mkdir -p ${CACHEDIR}

# if CACHEFILE doesn't exist
if [ ! -f ${CACHEFILE} ]; then
    getIndex
fi

# if CACHEFILE is outdated
if test `find "${CACHEFILE}" -mmin +30`; then
    getIndex
fi

# return results from all caches, allows for custom entries
cat ${CACHEDIR}/*.cache | sort | uniq
