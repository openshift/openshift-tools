# /usr/local/bin/start.sh will start the service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Add root folder
ADD root/ /root/

RUN yum install -y python2-boto3 \
                   python-requests \
                   MySQL-python \
                   python34 \
                   python34-mysql \
                   python2-botocore && \
    yum clean all

ADD scripts/ /usr/local/bin/

RUN mkdir -p /var/log/reports && \
    chmod -R g+rwX /etc/passwd /etc/group /var/log && \
    chmod -R 777 /usr/local/bin

# Start processes
CMD /usr/local/bin/start.sh
