#!/usr/bin/env bash

# Add excludes files to this list here.
# Space delimited
exclude_pattern_list=(
 'prometheus_client'
)

# Use the openshift-ansible .pylintrc
/usr/bin/wget https://raw.githubusercontent.com/openshift/openshift-ansible/master/git/.pylintrc -O jenkins/.pylintrc -q

oldrev=$1
newrev=$2

# Build a list of files to test
files_to_test=()

# Get a list of the files that are being submitted
for dfile in  $(/usr/bin/git diff --name-only "$oldrev" "$newrev" --diff-filter=ACM); do
  skip_file=false
  for exclude_pattern in "${exclude_pattern_list[@]}"; do
    #if [[ "${dfile}" == *"${exclude_file}"* ]]; then
    if [[ "${dfile}" =~ $exclude_pattern ]]; then
      skip_file=true
      break
    fi
  done

  if [ $skip_file == false ] && file $dfile | grep -q -i python; then
    files_to_test+=("$dfile")
  fi
done

# Check the files for pylint
if [ "${#files_to_test[@]}" -gt 0 ]; then
  /usr/bin/pylint --rcfile jenkins/.pylintrc "${files_to_test[@]}"
fi

# Exit status is captured by jenkins and
# determines build failure status
exit $?
