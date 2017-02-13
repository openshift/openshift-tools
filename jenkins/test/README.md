# OpenShift-tools automated testing
This directory contains the files used for the testing process of the openshift-tools CI.

## Adding to or modifying tests
Executable files added in `Validators/` will be run before rpms are built and installed. To run a test after rpms are installed, add the test to the `run_unit_tests.sh` file.

## Files
- Validators/
...Executable files within the validators directory are run to verify the changes in a pull request before building and installing rpms.
- Dockerfile
...This is the Dockerfile used to run the testing in an openshift environment. The `../openshift-tools-pr-automation-template.json` template specifies this Dockerfile to be used to run tests
- github_helpers.py
...A collection of helper functions used to communicate with the github v3 api during testing.
- run_tests.py
...The main entrypoint of testing. The dockerfile calls this script as its last instruction. This file handles consuming the github webhook, pulling in changes, running validators, building & installing rpms, and running unit tests.
- run_unit_tests.sh
...This executable contains all unit tests to be run on the oso-host-monitoring container after building & installing the openshift-tools rpms.
