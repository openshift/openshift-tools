FROM rhel7:latest

# get rid of subscript manager (we use our own mirrors)
RUN touch /var/run/rhsm ; rpm -evh subscription-manager

# creature comforts (make it feel like a normal linux environment)
ENV LANG en_US.UTF-8
ENV CONTAINER docker
ENV USER root
ENV HOME /root
ENV TERM xterm
WORKDIR /root
ADD bashrc /root/.bashrc

# setup epel repo
RUN rpm -ivh https://download-i2.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm

# setup yum repos
ADD setup-yum.sh /usr/local/bin/setup-yum.sh
RUN /usr/local/bin/setup-yum.sh

RUN yum clean metadata && \
    yum -y install ansible screen vim procps less ack tar psmisc && \
    yum -y update && \
    yum clean all

# Setup Screen
RUN chmod 777 /var/run/screen

# Setup Ansible
RUN echo -e '[local]\nlocalhost       ansible_connection=local\n' > /etc/ansible/hosts
