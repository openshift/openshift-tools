# /usr/local/bin/start.sh will start the service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Add root folder
ADD root/ /root/

# /root/rkhunter-2.4.2-1.x86_64.rpm \
# Local install of rkhunter RPM
RUN yum install -y rkhunter \
                   python2-boto3 \
                   python-requests \
                   python-openshift-tools \
                   python-openshift-tools-monitoring-zagg \
                   python2-botocore && \
    yum clean all

ADD scripts/ /usr/local/bin/

# Make mount points for rkhunter files, and configure rkhunter to work with this structure
RUN mkdir -p /etc/openshift_tools/ \
	     /var/local/rkhunter_chroot \
             /var/local/rkhunter_tmp \
             /var/local/rkhunter_tmp/rkhunter \
             /var/local/rkhunter_tmp/rkhunter/bin \
             /var/local/rkhunter_tmp/rkhunter/db \
             /var/local/rkhunter_tmp/rkhunter/etc \
             /var/local/rkhunter_tmp/rkhunter/scripts && \
    sed -i 's/\/var\/log\/rkhunter\/rkhunter.log/\/var\/local\/rkhunter_tmp\/rkhunter\/rkhunter.log/' /etc/logrotate.d/rkhunter && \
    sed -r -e 's%^(SCRIPTDIR)=.*%\1=/tmp/rkhunter/scripts%; s%^(LOGFILE)=.*%\1=/tmp/rkhunter/rkhunter.log%' /etc/rkhunter.conf > /var/local/rkhunter_tmp/rkhunter/etc/rkhunter.conf

# run as root user
USER 0

# Start processes
CMD /usr/local/bin/start.sh
