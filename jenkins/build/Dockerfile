FROM registry.ops.openshift.com/ops/oso-rhel7-host-monitoring:prod

# Add the openshift bot credentials to the build
ADD openshift-ops-bot/ /openshift-ops-bot/

# Add the rpm signing info to the build
ADD rpm-signing/ /rpm-signing/

# Add the s3 access credentials
ADD s3-access/ /s3-access/

# Set this so that the built image, when started, will sit and wait.
# This allows the resulting image to be easily reviewed. Normally, the image is thrown
# away, as only the build process is important.
# ENV OO_PAUSE_ON_START=true

RUN mkdir /builder && \
    git config --global push.default simple && \
    git clone https://github.com/openshift/openshift-tools /builder/openshift-tools && \
    cd /builder/openshift-tools && \
    git checkout stg && \
    cd /builder && \
    export PYTHONPATH=/builder/openshift-tools/jenkins/lib:$PYTHONPATH && \
    /usr/bin/python /builder/openshift-tools/jenkins/build/run_builds.py
