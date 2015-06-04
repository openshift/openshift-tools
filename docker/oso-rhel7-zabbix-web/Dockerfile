# Example docker run command
# docker run -ti --net=host --name web --rm=true oso-rhel7-zabbix-web
# /root/start.sh will then start the httpd.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

# Lay down the zabbix repository
RUN yum clean metadata && \
    yum install -y openshift-ops-yum-zabbix && \
    yum clean all

# Install zabbix from zabbix repo
RUN yum install -y zabbix-web-mysql && \
    yum -y update && \
    yum clean all

## WORK AROUND FOR PHP ZABBIX CONF MISSING
ADD zabbix.conf.php /etc/zabbix/web/

## Copy httpd.conf
ADD httpd.conf /etc/httpd/conf/

# Set the timezone in the php.ini file
RUN sed -r -ie 's/^;(date.timezone).*/\1 = America\/New_York/g' /etc/php.ini

# Start apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

