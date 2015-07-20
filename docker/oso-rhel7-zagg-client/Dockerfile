FROM oso-rhel7-ops-base:latest

RUN yum clean metadata && \
    yum install -y python-pip pcp pcp-conf pcp-testsuite \
        python-requests \
        python-openshift-tools-web \
        python-openshift-tools-monitoring \
        openshift-tools-scripts-monitoring \
        pcp-manager pcp-webapi python-pcp && \
    yum -y update && \
    yum clean all

# Ansible startup configuration playbook
ADD config.yml /root/config.yml

# Add the start script and tell the container to run it by default
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN time chmod -R o+rwX /boot /dev /etc /home /media /mnt /opt /root /run /srv /usr/lib/python*/site-packages/openshift*
