# Example docker run command
# docker run -ti --net=host --name web --rm=true oso-rhel7-zabbix-web
# /root/start.sh will then start the httpd.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while true ; do sleep 10 ; done

EXPOSE 8000

# Lay down the zabbix repository
RUN yum clean metadata && \
    yum install -y openshift-ops-yum-zabbix && \
    yum clean all

# Install zabbix from zabbix repo
RUN yum install -y zabbix-web-mysql mariadb && \
    yum -y update && \
    yum clean all

## WORK AROUND FOR PHP ZABBIX CONF MISSING
ADD zabbix.conf.php /etc/zabbix/web/

## Copy httpd.conf
ADD httpd.conf /etc/httpd/conf/

# Set the timezone in the php.ini file
RUN sed -r -ie 's/^;(date.timezone).*/\1 = America\/New_York/g' /etc/php.ini

# RHEL7.2 Fix for mod_auth_digest writing to /run/httpd/authdigest_shm.pid
RUN sed -i -e 's/^\(LoadModule auth_digest_module modules\/mod_auth_digest.so\)$/#\1/g' /etc/httpd/conf.modules.d/00-base.conf

# Start apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

# Fix v3 specific environment
# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN mkdir -p /run/httpd
RUN chmod -R g+rwX /etc/httpd /etc/passwd /usr/share/zabbix/ /run/ /var/log /etc/zabbix/web && \
    chgrp -R root /run/ /var/log /etc/zabbix/web 
