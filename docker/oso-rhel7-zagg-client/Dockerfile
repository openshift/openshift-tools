FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while true ; do sleep 10 ; done

RUN echo -e "\n\nalias oca='KUBECONFIG=/etc/openshift/master/admin.kubeconfig oc '" >> /root/.bashrc
RUN echo "alias oadma='KUBECONFIG=/etc/openshift/master/admin.kubeconfig oadm '" >> /root/.bashrc

RUN yum clean metadata && \
    yum install -y python-pip pcp pcp-conf pcp-testsuite \
        openshift \
        python-requests \
        python-openshift-tools-web \
        python-openshift-tools-monitoring \
        openshift-tools-scripts-monitoring \
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
