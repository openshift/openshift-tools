# /usr/local/bin/start.sh will start the service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

ADD scripts/ /usr/local/bin/

ADD root/ /root/

RUN mkdir -p /host/usr/bin /logs /var/log/journal

USER 0

# Start processes
CMD /usr/local/bin/start.sh
