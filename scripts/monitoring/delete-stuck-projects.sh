#!/bin/bash
# This is a workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1367432

# Look for any projects found during the last run of this script
if [ -f /tmp/stuck_projects ]; then
  projects_to_delete="$(cat /tmp/stuck_projects)"

  # If the project still exists, is empty, and contains nothing, delete it.
  for project in ${projects_to_delete}; do
    oc get project ${project} &> /dev/null

    if [ $? == 0 ] && [ -z "$(oc get all -n ${project})" ]; then
      oc get projects ${project} -o yaml
      oc delete project ${project}
    fi
  done
fi

# Get a list of all projects
oc get ns --template='{{ range .items }}{{.metadata.name}}{{ printf "\n" }}{{end}}' |sort > /tmp/namespaces

# Compare with a list of all projects containing rolebindings
oc get rolebindings --all-namespaces --template='{{ range .items }}{{.metadata.namespace}}{{ printf "\n" }}{{end}}' | sort -u > /tmp/namespaces_with_rolebindings

# The diff between those are the stuck projects, to be removed on the next run of this script
grep -Fxvf /tmp/namespaces_with_rolebindings /tmp/namespaces |grep -v -e kube-system -e default -e openshift-infra -e openshift > /tmp/stuck_projects
