FROM registry.ops.openshift.com/ops/oso-rhel7-host-monitoring:prod

# Add the openshift bot credentials to the build
ADD openshift-ops-bot/ /openshift-ops-bot/

# Add the admin whitelist to the build
ADD whitelist/ /whitelist/

# Set this so that the built image, when started, will sit and wait.
# This allows the resulting image to be easily reviewed. Normally, the image is thrown
# away, as only the build process is important.
# ENV OO_PAUSE_ON_START=true

RUN mkdir /validator && \
    git clone https://github.com/tiwillia/openshift-tools /validator/openshift-tools && \
    cd /validator/openshift-tools && \
    git config user.name validator && \
    git config user.email validator@localhost && \
    /usr/bin/python /validator/openshift-tools/jenkins/test/run_tests.py
