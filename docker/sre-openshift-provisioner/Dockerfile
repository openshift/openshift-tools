# Example docker run command
# docker run -ti --net=host --name web --rm=true sre-openshift-provisioner

FROM openshift/origin-ansible:latest

ARG SRE_OA_URL=https://github.com/openshift/openshift-ansible.git
ARG SRE_OA_BRANCH=release-3.11
ARG SRE_OA_CLONE_LOCATION=/usr/share/ansible/openshift-ansible
ARG SRE_TOOLS_URL=https://github.com/openshift/openshift-tools.git
ARG SRE_TOOLS_BRANCH=prod
ARG SRE_TOOLS_CLONE_LOCATION=/opt/openshift-tools

USER root

RUN yum -y install git

# Update the AWS client code so that operations like ec2_image work
RUN pip install dyn awscli botocore boto3 -U

RUN rm -rf ${SRE_OA_CLONE_LOCATION} && mkdir -p ${SRE_OA_CLONE_LOCATION}
RUN git clone ${SRE_OA_URL} ${SRE_OA_CLONE_LOCATION} && \
    cd ${SRE_OA_CLONE_LOCATION} && \
        git checkout ${SRE_OA_BRANCH}

RUN git clone ${SRE_TOOLS_URL} ${SRE_TOOLS_CLONE_LOCATION} && \
    cd ${SRE_TOOLS_CLONE_LOCATION} && \
        git checkout ${SRE_TOOLS_BRANCH}


COPY ansible.cfg /etc/ansible/ansible.cfg
RUN chmod 644 /etc/ansible/ansible.cfg

COPY provision_cluster.sh /usr/local/bin/provision_cluster.sh
RUN chmod 755 /usr/local/bin/provision_cluster.sh

CMD /usr/local/bin/provision_cluster.sh
