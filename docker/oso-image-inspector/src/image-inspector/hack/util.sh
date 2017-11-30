#!/bin/bash

# see https://github.com/openshift/origin/blob/master/hack/util.sh

# Provides simple utility functions

# tryuntil loops, retrying an action until it succeeds or times out after 90 seconds.
function tryuntil {
	timeout=$(($(date +%s) + 90))
	echo "++ Retrying until success or timeout: ${@}"
	while [ 1 ]; do
		if eval "${@}" >/dev/null 2>&1; then
			return 0
		fi
		if [[ $(date +%s) -gt $timeout ]]; then
			# run it one more time so we can display the output
			# for debugging, since above we /dev/null the output
			if eval "${@}"; then
				return 0
			fi
			echo "++ timed out"
			return 1
		fi
	done
}

# wait_for_command executes a command and waits for it to
# complete or times out after max_wait.
#
# $1 - The command to execute (e.g. curl -fs http://redhat.com)
# $2 - Optional maximum time to wait in ms before giving up (Default: 10000ms)
# $3 - Optional alternate command to determine if the wait should
#		exit before the max_wait
function wait_for_command {
	STARTTIME=$(date +%s)
	cmd=$1
	msg="Waiting for command to finish: '${cmd}'..."
	max_wait=${2:-10*TIME_SEC}
	fail=${3:-""}
	wait=0.2

	echo "[INFO] $msg"
	expire=$(($(time_now) + $max_wait))
	set +e
	while [[ $(time_now) -lt $expire ]]; do
	eval $cmd
	if [ $? -eq 0 ]; then
		set -e
		ENDTIME=$(date +%s)
		echo "[INFO] Success running command: '$cmd' after $(($ENDTIME - $STARTTIME)) seconds"
		return 0
	fi
	#check a failure condition where the success
	#command may never be evaulated before timing
	#out
	if [[ ! -z $fail ]]; then
		eval $fail
		if [ $? -eq 0 ]; then
		set -e
		echo "[FAIL] Returning early. Command Failed '$cmd'"
		return 1
		fi
	fi
	sleep $wait
	done
	echo "[ ERR] Gave up waiting for: '$cmd'"
	set -e
	return 1
}

# wait_for_url_timed attempts to access a url in order to
# determine if it is available to service requests.
#
# $1 - The URL to check
# $2 - Optional prefix to use when echoing a successful result
# $3 - Optional maximum time to wait before giving up (Default: 10s)
function wait_for_url_timed {
	STARTTIME=$(date +%s)
	url=$1
	prefix=${2:-}
	max_wait=${3:-10*TIME_SEC}
	wait=0.2
	expire=$(($(time_now) + $max_wait))
	set +e
	while [[ $(time_now) -lt $expire ]]; do
	out=$(curl --max-time 2 -fs $url 2>/dev/null)
	if [ $? -eq 0 ]; then
		set -e
		echo ${prefix}${out}
		ENDTIME=$(date +%s)
		echo "[INFO] Success accessing '$url' after $(($ENDTIME - $STARTTIME)) seconds"
		return 0
	fi
	sleep $wait
	done
	echo "ERROR: gave up waiting for $url"
	set -e
	return 1
}

# wait_for_file returns 0 if a file exists, 1 if it does not exist
#
# $1 - The file to check for existence
# $2 - Optional time to sleep between attempts (Default: 0.2s)
# $3 - Optional number of attemps to make (Default: 10)
function wait_for_file {
	file=$1
	wait=${2:-0.2}
	times=${3:-10}
	for i in $(seq 1 $times); do
	if [ -f "${file}" ]; then
		return 0
	fi
	sleep $wait
	done
	echo "ERROR: gave up waiting for file ${file}"
	return 1
}

# wait_for_url attempts to access a url in order to
# determine if it is available to service requests.
#
# $1 - The URL to check
# $2 - Optional prefix to use when echoing a successful result
# $3 - Optional time to sleep between attempts (Default: 0.2s)
# $4 - Optional number of attemps to make (Default: 10)
function wait_for_url {
	url=$1
	prefix=${2:-}
	wait=${3:-0.2}
	times=${4:-10}

	set_curl_args $wait $times

	set +e
	cmd="env -i CURL_CA_BUNDLE=${CURL_CA_BUNDLE:-} $(which curl) ${clientcert_args} -fs ${url}"
	for i in $(seq 1 $times); do
		out=$(${cmd})
		if [ $? -eq 0 ]; then
			set -e
			echo "${prefix}${out}"
			return 0
		fi
		sleep $wait
	done
	echo "ERROR: gave up waiting for ${url}"
	echo $(${cmd})
	set -e
	return 1
}

# set_curl_args tries to export CURL_ARGS for a program to use.
# will do a wait for the files to exist when using curl with
# SecureTransport (because we must convert the keys to a different
# form).
#
# $1 - Optional time to sleep between attempts (Default: 0.2s)
# $2 - Optional number of attemps to make (Default: 10)
function set_curl_args {
	wait=${1:-0.2}
	times=${2:-10}

	CURL_CERT=${CURL_CERT:-}
	CURL_KEY=${CURL_KEY:-}
	clientcert_args="${CURL_EXTRA:-} "

	if [ -n "${CURL_CERT}" ]; then
	 if [ -n "${CURL_KEY}" ]; then
	 if [[ `curl -V` == *"SecureTransport"* ]]; then
		 # Convert to a p12 cert for SecureTransport
		 export CURL_CERT_DIR=$(dirname "${CURL_CERT}")
		 export CURL_CERT_P12=${CURL_CERT_P12:-${CURL_CERT_DIR}/cert.p12}
		 export CURL_CERT_P12_PASSWORD=${CURL_CERT_P12_PASSWORD:-password}
		 if [ ! -f "${CURL_CERT_P12}" ]; then
		 wait_for_file "${CURL_CERT}" $wait $times
		 wait_for_file "${CURL_KEY}" $wait $times
		 openssl pkcs12 -export -inkey "${CURL_KEY}" -in "${CURL_CERT}" -out "${CURL_CERT_P12}" -password "pass:${CURL_CERT_P12_PASSWORD}"
		 fi
		 clientcert_args="--cert ${CURL_CERT_P12}:${CURL_CERT_P12_PASSWORD} ${CURL_EXTRA:-}"
	 else
		 clientcert_args="--cert ${CURL_CERT} --key ${CURL_KEY} ${CURL_EXTRA:-}"
	 fi
	 fi
	fi
	export CURL_ARGS="${clientcert_args}"
}

# Search for a regular expression in a HTTP response.
#
# $1 - a valid URL (e.g.: http://127.0.0.1:8080)
# $2 - a regular expression or text
function validate_response {
	url=$1
	expected_response=$2
	wait=${3:-0.2}
	times=${4:-10}

	set +e
	for i in $(seq 1 $times); do
	response=`curl $url`
	echo $response | grep -q "$expected_response"
	if [ $? -eq 0 ]; then
		echo "[INFO] Response is valid."
		set -e
		return 0
	fi
	sleep $wait
	done

	echo "[INFO] Response is invalid: $response"
	set -e
	return 1
}


# reset_tmp_dir will try to delete the testing directory.
# If it fails will unmount all the mounts associated with
# the test.
#
# $1 expression for which the mounts should be checked
reset_tmp_dir() {
	local sudo="${USE_SUDO:+sudo}"

	set +e
	${sudo} rm -rf ${BASETMPDIR} &>/dev/null
	if [[ $? != 0 ]]; then
		echo "[INFO] Unmounting previously used volumes ..."
		findmnt -lo TARGET | grep ${BASETMPDIR} | xargs -r ${sudo} umount
		${sudo} rm -rf ${BASETMPDIR}
	fi

	mkdir -p ${BASETMPDIR} ${LOG_DIR} ${ARTIFACT_DIR} ${FAKE_HOME_DIR} ${VOLUME_DIR}
	set -e
}

# kill_all_processes function will kill all
# all processes created by the test script.
function kill_all_processes()
{
	local sudo="${USE_SUDO:+sudo}"

	pids=($(jobs -pr))
	for i in ${pids[@]-}; do
		pgrep -P "${i}" | xargs $sudo kill &> /dev/null
		$sudo kill ${i} &> /dev/null
	done
}

# time_now return the time since the epoch in millis
function time_now()
{
	echo $(date +%s000)
}

# dump_container_logs writes container logs to $LOG_DIR
function dump_container_logs()
{
	if ! docker version >/dev/null 2>&1; then
		return
	fi

	mkdir -p ${LOG_DIR}

	echo "[INFO] Dumping container logs to ${LOG_DIR}"
	for container in $(docker ps -aq); do
		container_name=$(docker inspect -f "{{.Name}}" $container)
		# strip off leading /
		container_name=${container_name:1}
		if [[ "$container_name" =~ ^k8s_ ]]; then
			pod_name=$(echo $container_name | awk 'BEGIN { FS="[_.]+" }; { print $4 }')
			container_name=${pod_name}-$(echo $container_name | awk 'BEGIN { FS="[_.]+" }; { print $2 }')
		fi
		docker logs "$container" >&"${LOG_DIR}/container-${container_name}.log"
	done
}

# delete_empty_logs deletes empty logs
function delete_empty_logs() {
	# Clean up zero byte log files
	find "${ARTIFACT_DIR}" "${LOG_DIR}" -type f -name '*.log' \( -empty \) -delete
}

# truncate_large_logs truncates large logs so we only download the last 20MB
function truncate_large_logs() {
	# Clean up large log files so they don't end up on jenkins
	local large_files=$(find "${ARTIFACT_DIR}" "${LOG_DIR}" -type f -name '*.log' \( -size +20M \))
	for file in ${large_files}; do
		cp "${file}" "${file}.tmp"
		echo "LOGFILE TOO LONG, PREVIOUS BYTES TRUNCATED. LAST 20M BYTES OF LOGFILE:" > "${file}"
		tail -c 20M "${file}.tmp" >> "${file}"
		rm "${file}.tmp"
	done
}

# Handler for when we exit automatically on an error.
# Borrowed from https://gist.github.com/ahendrix/7030300
ii::log::errexit() {
	local err="${PIPESTATUS[@]}"

	# If the shell we are in doesn't have errexit set (common in subshells) then
	# don't dump stacks.
	set +o | grep -qe "-o errexit" || return

	set +o xtrace
	local code="${1:-1}"
	ii::log::error_exit "'${BASH_COMMAND}' exited with status $err" "${1:-1}" 1
}

ii::log::install_errexit() {
	# trap ERR to provide an error handler whenever a command exits nonzero this
	# is a more verbose version of set -o errexit
	trap 'ii::log::errexit' ERR

	# setting errtrace allows our ERR trap handler to be propagated to functions,
	# expansions and subshells
	set -o errtrace
}

# Print out the stack trace
#
# Args:
#	 $1 The number of stack frames to skip when printing.
ii::log::stack() {
	local stack_skip=${1:-0}
	stack_skip=$((stack_skip + 1))
	if [[ ${#FUNCNAME[@]} -gt $stack_skip ]]; then
	echo "Call stack:" >&2
	local i
	for ((i=1 ; i <= ${#FUNCNAME[@]} - $stack_skip ; i++))
	do
		local frame_no=$((i - 1 + stack_skip))
		local source_file=${BASH_SOURCE[$frame_no]}
		local source_lineno=${BASH_LINENO[$((frame_no - 1))]}
		local funcname=${FUNCNAME[$frame_no]}
		echo "	$i: ${source_file}:${source_lineno} ${funcname}(...)" >&2
	done
	fi
}

# Log an error and exit.
# Args:
#	 $1 Message to log with the error
#	 $2 The error code to return
#	 $3 The number of stack frames to skip when printing.
ii::log::error_exit() {
	local message="${1:-}"
	local code="${2:-1}"
	local stack_skip="${3:-0}"
	stack_skip=$((stack_skip + 1))

	local source_file=${BASH_SOURCE[$stack_skip]}
	local source_line=${BASH_LINENO[$((stack_skip - 1))]}
	echo "!!! Error in ${source_file}:${source_line}" >&2
	[[ -z ${1-} ]] || {
	echo "	${1}" >&2
	}

	ii::log::stack $stack_skip

	echo "Exiting with status ${code}" >&2
	exit "${code}"
}

ii::log::with-severity() {
  local msg=$1
  local severity=$2

  echo "[$2] ${1}"
}

ii::log::info() {
  ii::log::with-severity "${1}" "INFO"
}

ii::log::warn() {
  ii::log::with-severity "${1}" "WARNING"
}

ii::log::error() {
  ii::log::with-severity "${1}" "ERROR"
}

find_files() {
	find . -not \( \
		\( \
		-wholename './_output' \
		-o -wholename './_tools' \
		-o -wholename './.*' \
		-o -wholename './pkg/assets/bindata.go' \
		-o -wholename './pkg/assets/*/bindata.go' \
		-o -wholename './pkg/bootstrap/bindata.go' \
		-o -wholename './openshift.local.*' \
		-o -wholename '*/Godeps/*' \
		-o -wholename '*/vendor/*' \
		-o -wholename './assets/bower_components/*' \
		\) -prune \
	\) -name '*.go' | sort -u
}

# Asks golang what it thinks the host platform is.  The go tool chain does some
# slightly different things when the target platform matches the host platform.
ii::util::host_platform() {
  echo "$(go env GOHOSTOS)/$(go env GOHOSTARCH)"
}

ii::util::sed() {
  if [[ "$(go env GOHOSTOS)" == "darwin" ]]; then
  	sed -i '' "$@"
  else
  	sed -i'' "$@"
  fi
}

ii::util::base64decode() {
  if [[ "$(go env GOHOSTOS)" == "darwin" ]]; then
  	base64 -D $@
  else
  	base64 -d $@
  fi
}

ii::util::get_object_assert() {
  local object=$1
  local request=$2
  local expected=$3

  res=$(eval oc get $object -o go-template=\"$request\")

  if [[ "$res" =~ ^$expected$ ]]; then
      echo "Successful get $object $request: $res"
      return 0
  else
      echo "FAIL!"
      echo "Get $object $request"
      echo "  Expected: $expected"
      echo "  Got:      $res"
      return 1
  fi
}
