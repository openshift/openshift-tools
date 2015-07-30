# Example docker run command
# docker run -p 10050:10050 -p 10050:10050 -p 80:80 -p 443:443 oso-rhel7-zaio
# /root/start.sh will then start the mysqldb, zabbix, and httpd services.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

# Install mariadb mariadb-server
RUN yum install -y  mariadb mariadb-server && \
    yum -y update && \
    yum clean all

EXPOSE 3306

# Add mysql files
ADD mariadb-prepare-db-dir /usr/libexec/
ADD my.cnf /etc/

# Add zabbix mysql files
ADD createdb.sh /root/


# Start mysqld, zabbix, and apache
ADD start.sh /usr/local/bin/
RUN setcap cap_dac_override,cap_chown,cap_fowner+ep /usr/local/bin/start.sh
CMD /usr/local/bin/start.sh

# Fix perms
RUN chmod -R g+rwX /etc/passwd /etc/my.cnf /var/log /run /var/lib/mysql && \
          chgrp -R root /var/log /run /var/lib/mysql
RUN chmod -R 777 /var
