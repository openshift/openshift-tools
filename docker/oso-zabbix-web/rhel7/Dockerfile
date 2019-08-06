# Example docker run command
# docker run -ti --net=host --name web --rm=true oso-rhel7-zabbix-web
# /root/start.sh will then start the httpd.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

EXPOSE 8000

ADD zabbix.repo /etc/yum.repos.d/

# Install zabbix from zabbix repo
RUN yum-install-check.sh -y zabbix-web-mysql mariadb && \
    yum -y update && \
    yum clean all

ADD root/ /root/

## WORK AROUND FOR PHP ZABBIX CONF MISSING
ADD zabbix.conf.php /etc/zabbix/web/

## Copy httpd.conf
ADD httpd.conf /etc/httpd/conf/

# Set the timezone in the php.ini file
RUN sed -r -i -e 's/^;(date.timezone).*/\1 = America\/New_York/g' /etc/php.ini

# Disable exposure of php version information
RUN sed -i 's/expose_php = .*/expose_php = Off/g' /etc/php.ini

# RHEL7.2 Fix for mod_auth_digest writing to /run/httpd/authdigest_shm.pid
RUN sed -i -e 's/^\(LoadModule auth_digest_module modules\/mod_auth_digest.so\)$/#\1/g' /etc/httpd/conf.modules.d/00-base.conf

# increasing the memory limit for php, so big queries have a better chance succeeding
RUN sed -i -e 's/php_value memory_limit 128M/php_value memory_limit 512M/g' /etc/httpd/conf.d/zabbix.conf

# php installs this with root:apache, but we are not using apache group, so it throws errors on php_session creation
RUN chown root:root /var/lib/php/session

# adding redirect to the main apache config, so it will send every request to the /zabbix folder
ADD welcome.conf /etc/httpd/conf.d/

# Start apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

# Fix v3 specific environment
# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN mkdir -p /run/httpd
RUN chmod -R g+rwX /etc/httpd /etc/passwd /usr/share/zabbix/ /run/ /var/log /etc/zabbix/web && \
    chgrp -R root /run/ /var/log /etc/zabbix/web 
