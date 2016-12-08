#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 

# Example docker run command
# docker run -ti --net=host --name web --rm=true oso-rhel7-saml-sso
# /root/start.sh will then start the httpd.

FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

EXPOSE 8443

ADD prep_simplesaml.sh start.sh /usr/local/bin/

# Install SimpleSAML and modules from RPMs, then run our setup/hardening script for SimpleSAML
RUN yum install -y \
        httpd \
        mod_ssl \
        openshift-tools-web-simplesamlphp-modules \
        openssh-server \
        oso-simplesamlphp \
        php php-cli \
        php-google-apiclient \
        php-pecl-memcache \
        php-pecl-yaml \
        && \
    yum -y update && yum clean all && \
    prep_simplesaml.sh && \
    ln -sf /usr/share/simplesamlphp/modules/authorizeyaml/bin/get_saml_token.php /usr/local/bin/get_saml_token


# Copy config files
ADD sshd_config /etc/ssh/sshd_config

# Copy index redirect page and readyness/liveness probe handler
ADD index.php status.php /var/www/html/

# Start apache & sshd
CMD /usr/local/bin/start.sh

# Add config file templates and startup playbook
ADD root/ /root/

# Fix v3 specific environment
# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN mkdir -p /run/httpd && \
    chmod -R g+rwX /etc/httpd /etc/passwd /etc/group /run /var/log /usr/share/simplesamlphp/config && \
    chgrp -R root /run/ /var/log /var/lib/php/session && \
    ansible-playbook /root/build.yaml && \
    rm -rf /root/.ansible
