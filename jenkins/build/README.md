# Openshift-tools automated builds

This feature has not yet been implemented. 

The files in this directory are intended to control the rpm building and pushing process that would occur automatically when changes are merged into each of the branches int, stg, and prod.

Ideally, the Dockerfile in this directory would be specified by a new build in the `../openshift-tools-pr-automation-template.json`. The Dockerfile would set up an environment, similar to the testing environment, and then would run a script that would perform the official rpm builds. After building rpms with tito, rpms would be pushed to a yum repo. Image re-builds would be started, which would consume the yum repo with the new rpms. After successfully building images, they would be pushed to the registry and running containers would update to use the new image.
