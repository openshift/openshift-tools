# /usr/local/bin/start.sh will start the memcached service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while true ; do sleep 10 ; done || :

# Add necessary permissions to add arbitrary user
RUN chmod -R g+rwX /etc/passwd /etc/group

# Install memcached
RUN yum -y install python-pip \
        python-requests\
        pyOpenSSL \
        openssl \
        openssh-server \
        python2-boto3 \
        python-openshift-tools \
        python-openshift-tools-monitoring-zagg \
        python-openshift-tools-ansible \
        python-openshift-tools-web \
        python-beautifulsoup4 \
        openshift-tools-scripts \
        openshift-tools-scripts-monitoring-zagg-client \
        openshift-tools-scripts-iam-tools && \
    yum clean all

# Add root folder
ADD root/ /root/

# Add loop scripts
ADD ops-run-in-loop start.sh /usr/local/bin/

# Create ops-runner.log file with proper permissions
# Create monitor-sso.log file with proper permissions
# Create symlinks to secrets
RUN touch /var/log/ops-runner.log && chmod 664 /var/log/ops-runner.log && \
    touch /var/log/monitor-sso.log && chmod 664 /var/log/monitor-sso.log && \
    ln -sf /secrets/aws-accounts.txt /etc/openshift_tools/aws_accounts.txt && \
    ln -sf /secrets/sso-config.yaml /etc/openshift_tools/sso-config.yaml && \
    ln -sf /secrets/zagg-client.yaml /etc/openshift_tools/zagg_client.yaml

# Start memcached
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
