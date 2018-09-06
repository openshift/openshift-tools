# /usr/local/bin/start.sh will start the service

FROM openshifttools/oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Add root folder
ADD root/ /root/

# Local install of psad RPM
RUN yum install -y python2-boto3 \
                   systemd-python \
                   golang \
                   gcc \
                   git \
                   whois \
                   iproute \
                   net-tools \
                   perl-Data-Dumper \
                   perl-IPTables-ChainMgr \
                   perl-IPTables-Parse \
                   perl-Date-Calc \
                   perl-Unix-Syslog \
                   /root/psad-2.4.2-1.x86_64.rpm \
                   python-requests \
                   openscap-scanner \
                   python-openshift-tools \
                   python-openshift-tools-monitoring-zagg \
                   python34 \
                   python34-pip \
                   python34-libs \
                   python34-devel \
                   python34-PyYAML \
                   python2-pip \
                   python2-devel \
                   python2-botocore && \
    yum clean all

ADD scripts/ /usr/local/bin/

# Configure monitoring utilities, install prometheus
RUN pip3 install psutil prometheus_client && \
    pip install psutil prometheus_client && \
    setcap cap_net_raw,cap_net_admin+p /usr/sbin/xtables-multi

EXPOSE 8080

# run as root user
USER 0

# Start processes
CMD /usr/local/bin/start.sh
