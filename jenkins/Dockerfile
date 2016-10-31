FROM centos
#USER default

RUN yum install -y git
RUN git clone https://github.com/tiwillia/openshift-tools ~/openshift-tools
WORKDIR ~/openshift-tools
ENTRYPOINT ~/openshift-tools/jenkins/run_pr_validation.sh
