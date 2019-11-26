FROM registry.reg-aws.openshift.com:443/ops/oso-rhel7-host-monitoring:prod

# Add the openshift bot credentials to the build
ADD openshift-ops-bot/ /openshift-ops-bot/

# Add the admin whitelist to the build
ADD whitelist/ /whitelist/

# Set this so that the built image, when started, will sit and wait.
# This allows the resulting image to be easily reviewed. Normally, the image is thrown
# away, as only the build process is important.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Add github via pip
RUN pip install PyGithub

RUN mkdir /validator && \
    git clone https://github.com/openshift/openshift-tools /validator/openshift-tools && \
    cd /validator/openshift-tools && \
    git checkout stg && \
    git config user.name validator && \
    git config user.email validator@localhost && \
    /usr/bin/python /validator/openshift-tools/jenkins/test/run_tests.py
