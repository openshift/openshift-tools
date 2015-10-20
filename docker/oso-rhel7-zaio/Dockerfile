# Example docker run command
# docker run -p 10050:10050 -p 10051:10051 -p 80:80 -p 443:443 oso-rhel7-zaio
# /usr/local/bin/start.sh will then start the mysqldb, zabbix, and httpd services.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

# Lay down the zabbix repository
RUN yum clean metadata && \
    yum install -y openshift-ops-yum-zabbix && \
    yum clean all

# Install zabbix from zabbix repo
RUN yum install -y mod_ssl zabbix-server-mysql zabbix-sender zabbix-agent zabbix-web-mysql mariadb mariadb-server && \
    yum -y update && \
    yum clean all

# WORK AROUND FOR SQL SCRIPTS ARE MISSING
ADD zabbix/db_create/zdata /usr/share/doc/zabbix-server-mysql-2.4.5/create/

# Add mysql files
ADD mariadb-prepare-db-dir /usr/libexec/
ADD my.cnf /etc/

# Add zabbix mysql files
ADD zabbix/db_create/createdb.sh /root/
ADD zabbix/db_create/create_zabbix.sql /root/

# Lay down zabbix conf
ADD zabbix/conf/zabbix_server.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agentd.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agent.conf /etc/zabbix/

# Set the timezone in the php.ini file
RUN sed -r -ie 's/^;(date.timezone).*/\1 = America\/New_York/g' /etc/php.ini

# Zabbix web
ADD zabbix/conf/zabbix.conf.php /etc/zabbix/web/

# Start mysqld, zabbix, and apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
