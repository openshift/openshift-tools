base_sha=$PRV_BASE_SHA
remote_sha=$PRV_REMOTE_SHA

# Overwrite sha's with provided command-line arugments
if [ -n $1 ]; then
    base_sha=$1
fi
if [ -n $2 ]; then
    remote_sha=$2
fi

# Download the latest yaml validation script
curl https://raw.githubusercontent.com/openshift/openshift-ansible/master/git/yaml_validation.py -o jenkins/test/validators/yaml_validation.py 2>&1

if [ -e jenkins/test/validators/yaml_validation.py ];
then
  # The python validation script requires, but just throws away, the third argument.
  python jenkins/test/validators/yaml_validation.py base_sha remote_sha "nothing"
else
  exit 1
fi

exit $?

