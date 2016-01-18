FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while true ; do sleep 10 ; done || :

# PCP
##################
# install pcp-collector and it's dependencies, clean the cache.
RUN yum install -y pcp pcp-conf pcp-collector xz && yum clean all
# Run in the container as root - avoids PCP_USER mismatches
RUN sed -i -e 's/PCP_USER=.*$/PCP_USER=root/' -e 's/PCP_GROUP=.*$/PCP_GROUP=root/' /etc/pcp.conf

# Disable service advertising - no avahi daemon in the container
# (dodges warnings from pmcd attempting to connect during startup)
RUN . /etc/pcp.conf && echo "-A" >> $PCP_PMCDOPTIONS_PATH

# denote this as a container environment, for rc scripts
ENV PCP_CONTAINER_IMAGE pcp-collector
ENV NAME pcp-collector
ENV IMAGE pcp-collector
ENV PATH /usr/share/pcp/lib:/usr/libexec/pcp/bin:$PATH

# script to watch health of pmcd
ADD check-pmcd-status.sh /usr/local/bin/check-pmcd-status.sh
##################

RUN echo -e "\n\nalias oca='KUBECONFIG=/etc/openshift/master/admin.kubeconfig oc '" >> /root/.bashrc
RUN echo "alias oadma='KUBECONFIG=/etc/openshift/master/admin.kubeconfig oadm '" >> /root/.bashrc

RUN yum clean metadata && \
    yum install -y python-pip pcp pcp-conf pcp-testsuite \
        openshift \
        python-requests \
        python-openshift-tools \
        python-openshift-tools-monitoring-pcp \
        python-openshift-tools-monitoring-docker \
        python-openshift-tools-monitoring-zagg \
        python-openshift-tools-monitoring-openshift \
        python-openshift-tools-ansible \
        python-openshift-tools-web \
        openshift-tools-scripts \
        openshift-tools-scripts-monitoring-pcp \
        openshift-tools-scripts-monitoring-docker \
        openshift-tools-scripts-monitoring-zagg-client \
        openshift-tools-scripts-monitoring-aws \
        openshift-tools-scripts-monitoring-openshift \
        pcp-manager pcp-webapi python-pcp \
        openvswitch \
        docker-python && \
    yum -y update && \
    yum clean all

# Ansible startup configuration playbook
ADD root /root

# FIXME: These are vendor libs that need to be packaged and installed via RPM.
ADD vendor/prometheus_client /usr/lib/python2.7/site-packages/prometheus_client/

# FIXME: These are ugly quick hacked together monitoring scripts
# They need to be removed and replaced by prototype monitoring scripts later on
# Or refactored into libs and added to rpms
ADD monitoring_scripts /usr/local/bin
RUN chmod +x /usr/local/bin/cron-send*

# Add the start script and tell the container to run it by default
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
