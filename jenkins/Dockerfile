FROM centos
#USER default

RUN yum install -y git python
RUN git clone https://github.com/tiwillia/openshift-tools /root/openshift-tools
WORKDIR /root/openshift-tools/jenkins/
ENTRYPOINT /root/openshift-tools/jenkins/run_pr_validation.sh
