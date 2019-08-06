FROM rhel7:7.6

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

ADD usr_local_bin/* /usr/local/bin/

# setup yum repos
RUN /usr/local/bin/setup-yum.sh
RUN yum repolist --disablerepo=* && \
    yum-config-manager --disable \* > /dev/null && \
    yum-config-manager --enable rhel-7-server-rpms rhel-7-server-extras-rpms

# creature comforts (make it feel like a normal linux environment)
ENV LANG en_US.UTF-8
ENV CONTAINER docker
ENV USER root
ENV HOME /root
ENV TERM xterm
WORKDIR /root
ADD root/bashrc /root/.bashrc
ADD root/pdbrc /root/.pdbrc

# Make working in Python nice
ADD root/pythonrc /root/.pythonrc
ENV PYTHONSTARTUP=/root/.pythonrc

# setup epel repo
RUN rpm -ivh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm


RUN yum clean metadata && \
    yum -y update && \
    yum-install-check.sh -y wget iputils cronie ansible-2.4.2.0 vim-enhanced procps-ng less ack tar psmisc python2-scandir lsof && \
    yum clean all

# Stay on Ansible 2.4 when updating packages
RUN echo "exclude=ansible" >> /etc/yum.conf

# Setup locales.  It comes broken (probably a size issue) by default in the docker image.
RUN yum -y reinstall glibc-common &&  \
    yum clean all  && \
    mv -f /usr/lib/locale/locale-archive /usr/lib/locale/locale-archive.tmpl  && \
    /usr/sbin/build-locale-archive

# Setup Cron
ADD pamd.crond /etc/pam.d/crond

# Setup Ansible
ADD ansible.cfg /etc/ansible/ansible.cfg
RUN echo -e '[local]\nlocalhost       ansible_connection=local\n' > /etc/ansible/hosts

# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN chmod -R g+rwX /root/


# This is a temporary fix, until we find something that works better, PRs are welcome
# The reason for this change is that some repos get disabled, especially with the latest rhel74 image
# so this was added so other containers can start with their repos properly enabled
# this change might have been that there was a bug in yum-config-manager previously, that didn't
# actually disable every repo and now it does, or maybe something else, further research is required
RUN yum-config-manager --enable rhel-7-server-rpms rhel-7-server-extras-rpms epel
