FROM rhel7:latest

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

RUN yum -y remove subscription-manager && \
    yum clean metadata && \
    yum -y install ansible vim procps less ack tar psmisc && \
    yum -y update && \
    yum clean all
