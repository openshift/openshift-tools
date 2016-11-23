# /usr/local/bin/start.sh will start the memcached service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while true ; do sleep 10 ; done || :

# Add necessary permissions to add arbitrary user
RUN chmod -R g+rwX /etc/passwd /etc/group

# Install memcached
RUN yum -y install python-pip \
        pcp \
        pcp-conf \
        pcp-testsuite \
        python-requests\
        pyOpenSSL \
        openssl \
        openssh-server \
        python2-boto3 \
        python-beautifulsoup4 \
        python-openshift-tools \
        python-openshift-tools-monitoring-pcp \
        python-openshift-tools-monitoring-docker \
        python-openshift-tools-monitoring-zagg \
        python-openshift-tools-monitoring-openshift \
        python-openshift-tools-ansible \
        python-openshift-tools-web \
        openshift-tools-scripts \
        openshift-tools-scripts-monitoring-zagg-client \
        openshift-tools-scripts-iam-tools && \
    yum clean all

# Add root folder
ADD root/ /root/

# Add loop scripts
ADD ops-run-in-loop start.sh /usr/local/bin/

# Create monitor-sso.log file with proper permissions
RUN touch /var/log/monitor-sso.log && chmod 664 /var/log/monitor-sso.log

# Start memcached
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
