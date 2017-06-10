FROM oso-rhel7-ops-base:latest

# install ClamAV scanner and base signature database
RUN yum-install-check.sh -y \
        clamav \
        clamav-data \
        && \
    yum -y update && yum clean all

ADD root/ /root/

# build boater binary
RUN yum-install-check.sh --enablerepo=rhel-7-server-optional-rpms -y git golang glide && \
    cd /root/go/src/boater && \
    GOPATH=/root/go glide install && \
    ln -s vendor/github.com/dmage/boater/main.go && \
    GOPATH=/root/go go build && \
    mv boater /usr/local/bin && \
    cd /root && \
    rm -rf /root/go /root/.glide && \
    yum -y history undo last && \
    yum clean all
