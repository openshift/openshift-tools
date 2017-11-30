FROM travis/image-inspector-base
RUN yum install -y \
    git \
    which \
    make
ENV GOPATH=/go
COPY . /go/src/github.com/openshift/image-inspector
WORKDIR /go/src/github.com/openshift/image-inspector
RUN make install-travis
# this is necessary because cgo is disabled in our container.
# to detect races, enable CGO and install gcc
ENV DETECT_RACES=false
ENTRYPOINT make