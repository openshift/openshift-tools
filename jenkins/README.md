# Continuous Integration Automation

The files within this directory are used to set up automation around testing, building, and deploying changes to components in the openshift-tools repository.

### How it works
When a pull request is submitted to the openshift-tools repository on github, a webhook starts a job on a persistent jenkins instance running in an openshift environment. The job is a simple jenkins pipeline using the `Jenkinsfile` in this directory. The pipeline determines the action to take based on the action in the webhook. When a test is necessary, the jenkins pipeline starts a build on the openshift environment titled `openshift-tools-test` and outputs the build logs to the pipeline's logs.

The `openshift-tools-test` build is defined in the `openshift-tools-pr-automation-template.json` template. The build mounts a secret containing the github bot user credentials, then starts a docker build using the Dockerfile `test/Dockerfile`. This build runs from the oso-host-monitoring container and clones the openshift-tools repository. Once the environment is set up, the build runs the `test/run_tests.py` script. This script merges in the changes defined in the github webhook payload and defines several environment variables for consumption by a suite of validators. Each `.py` or .sh` file in `test/validators` is run with these environment varibles.

The script will then submit a comment to the pull request indiciating whether all of the validators passed or if one or more of them failed. The build will exist successfully if all validators pass. When the build completes, so does the jenkins pipeline. The build in jenkins is also marked as a success only if all validators pass.

### Requirements
- An OpenShift instance running at least Openshift 3.2
- Peristent storage configured and available to the user on Openshift
- External access to apps running on the OpenShift instance (github has to be able to reach jenkins at a persistent address)
- Access to configure github webhooks for the github repository

### Configuration
1. In an openshift environment, deploy a persistent jenkins instance using the [jenkins-persistent template]( https://raw.githubusercontent.com/openshift/origin/master/examples/jenkins/jenkins-persistent-template.json)

2. Deploy the builds and secrets in the openshift environment using the `openshift-tools-pr-automation-template.json` in this directory. A username and oauth token for a github user will be required.

3. Log into the jenkins instance using your openshift credentials and navigate to 'Manage Jenkins' > 'Configure Global Security'. Under 'Access Control' > 'Authorization', select the radio button 'Logged-in users can do anything'. Ensure the 'Allow anonymous read access' box remains checked. Save the changes.

4. In Jenkins, create a new jenkins pipeline job. Configure the following:
  1. Check the 'This project is parameterized' box and add a 'String Parameter' with the Name 'payload' (case-sensitive). Leave all other boxes empty.
  2. Under 'Build Triggers', check the 'Trigger builds remotely' checkbox and specify any string to use as the authorization token. This same token will be used later to configure the github webhook.
  3. Under 'Pipeline', select 'Pipeline script from SCM' as the pipeline definition. Choose 'Git' as the SCM and specify `https://github.com/openshift/openshift-tools` as the repository url. Leave the 'Branches to build' blank. For the 'Script path', set to 'jenkins/Jenkinsfile'
  4. Save the job
    
5. In github, navigate to the settings for openshift-tools with administrator permissions. Under webhooks, create a new webhook and configure the following:
  1. The Payload URL will be the url of the jenkins build trigger configured earlier. Here is an example where 'someuniquestring' is specified as the build trigger token: `https://jenkins-exampleproject.example.com/job/job_name/buildWithParameters?token=someuniquestring`
  2. Set the 'Content type' to `application/x-www-form-urlencoded`. This enabled the webhook payload to be sent as a parameter to the jenkins job.
  3. Under "Which events would you like to trigger", select only 'Pull request'.
  4. Check the 'Active' box to ensure the github webhook is active
  5. Hit 'Update webhook' to save the changes.
