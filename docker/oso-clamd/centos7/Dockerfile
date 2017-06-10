#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 

# Example docker run command
# docker run -ti --net=host --name web --rm=true oso-centos7-clamd

FROM openshifttools/oso-centos7-ops-clambase:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Install clamd
RUN yum-install-check.sh -y \
        clamav-server \
        && \
    yum -y update && yum clean all

# Start clamd
CMD /usr/sbin/clamd

ADD clamd.conf /etc/

# Fix v3 specific environment
# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN mkdir -p /var/log/clamav && \
    touch /var/log/clamav/clamd.log && \
    chmod -R g+rwX /var/run /var/log && \
    chgrp -R root /var/run/ /var/log && \
    echo clam:x:10000:0:USER:/root:/bin/bash >> /etc/passwd
#    ansible-playbook /root/build.yaml && \
#    rm -rf /root/.ansible
