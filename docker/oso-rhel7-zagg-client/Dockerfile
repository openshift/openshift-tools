FROM oso-rhel7-ops-base:latest

RUN yum clean metadata && \
    yum install -y python-pip pcp pcp-conf pcp-testsuite \
        openshift \
        python-requests \
        python-openshift-tools-web \
        python-openshift-tools-monitoring \
        openshift-tools-scripts-monitoring \
        pcp-manager pcp-webapi python-pcp \
        docker-python && \
    yum -y update && \
    yum clean all

# Ansible startup configuration playbook
ADD root /root

# FIXME: These are ugly quick hacked together monitoring scripts
# They need to be removed and replaced by prototype monitoring scripts later on
# Or refactored into libs and added to rpms
ADD monitoring_scripts /usr/local/bin
RUN chmod +x /usr/local/bin/cron-send*

# Add the start script and tell the container to run it by default
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
