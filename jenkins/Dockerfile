FROM centos
#USER default

RUN yum install -y git
WORKDIR ~/openshift-tools
RUN git clone https://github.com/tiwillia/openshift-tools
ENTRYPOINT ~/openshift-tools/jenkins/run_pr_validation.sh
