#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 

# Example docker run command
# docker run -ti --net=host --name web --rm=true oso-rhel7-clamd-update

FROM oso-rhel7-ops-clambase:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

ADD start.sh /usr/local/bin/
ADD clamd.conf /etc/clamd.conf

# Start updater script
CMD /usr/local/bin/start.sh

# Add config file templates and startup playbook
ADD root/ /root/

# Fix v3 specific environment
# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
# Also, make symlinks to CAs that boater will need to talk to the cluster registry
RUN chmod -R g+rwX /etc/passwd /etc/group /run /var/log /etc/pki/ca-trust/extracted/{pem,openssl,java} && \
    ln -sf /token/ca.crt         /etc/pki/ca-trust/source/anchors/cluster-ca.pem && \
    ln -sf /token/service-ca.crt /etc/pki/ca-trust/source/anchors/service-ca.pem && \
    chgrp -R root /run/ /var/log
