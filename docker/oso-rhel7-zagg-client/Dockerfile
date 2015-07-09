FROM oso-rhel7-ops-base:latest

RUN yum clean metadata && \
    yum install -y python-pip pcp pcp-conf pcp-testsuite \
        cronie \
        python-requests \
        python-openshift-tools-web \
        python-openshift-tools-monitoring \
        openshift-tools-scripts-monitoring \
        pcp-manager pcp-webapi python-pcp && \
    yum clean all

ADD ops-zagg-client.cron /etc/cron.d/ops-zagg-client

# Start cron
ADD start.sh /usr/local/bin/
RUN chmod 775 /usr/local/bin/start.sh
CMD /usr/local/bin/start.sh
