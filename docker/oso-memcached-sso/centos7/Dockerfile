# /usr/local/bin/start.sh will start the memcached service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Install memcached
RUN yum -y install memcached && \
    yum clean all

# Expose port 11211
EXPOSE 11211

# Add root folder
ADD root/ /root/

# Start memcached
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

# Add necessary permissions to add arbitrary user
RUN chmod -R g+rwX /etc/passwd /etc/group
