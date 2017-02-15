# OpenShift-Tools CI

The files within this directory are used to set up automation around testing, building, and deploying changes to components in the openshift-tools repository.

### Using the CI as a developer
Upon submitting a pull request, tests will automatically be started for the changes in the pull request as long as the user who opened the pull request is on the user or organization whitelist. There may be some delay between the tests starting and the pull request being updated as the docker build initialization can take some time. Once testing is completely, the pull request will be updated with the result. The last commit will be marked with success or failure and a link to the test output.

To manually run tests for a pull request, a whitelisted user can comment the term `[test]` to initiate testing. Testing will also be initiated any time the pull request commits are updated.

### How it works
When a pull request is submitted to the openshift-tools repository on github, a webhook starts a job on a persistent jenkins instance running in an openshift environment. The job is a simple jenkins pipeline using the `Jenkinsfile` in this directory. The pipeline determines the action to take based on the `action` field and some other details in the webhook. When a test is necessary, the jenkins pipeline starts a build on the openshift environment titled `openshift-tools-test` and outputs the build logs to the pipeline's logs.

Tests will be run whenever a pull request is opened, reopened, or "synchronized" (a commit is added, subtracted, or amended). Tests can also be manually performed by commenting on the pull request with the term '[test]' with a whitelisted user.

The `openshift-tools-test` build is defined in the `openshift-tools-pr-automation-template.json` template. The build mounts a secret containing the github bot user credentials, then starts a docker build using the Dockerfile `test/Dockerfile`. This build runs from the oso-host-monitoring container and clones the openshift-tools repository. Once the environment is set up, the build runs the `test/run_tests.py` script. This script merges in the changes defined in the github webhook payload and defines several environment variables for consumption by a suite of validators. Each `.py` or .sh` file in `test/validators` is run with these environment varibles.

The script will then submit a comment to the pull request indiciating whether all of the validators passed or if one or more of them failed. The build will exist successfully if all validators pass. When the build completes, so does the jenkins pipeline. The build in jenkins is also marked as a success only if all validators pass.

### Requirements
- An OpenShift instance running at least Openshift 3.2
- Peristent storage configured and available to the user on Openshift
- External access to apps running on the OpenShift instance (github has to be able to reach jenkins at a persistent address)
- Access to configure github webhooks for the github repository

### Configuration
1. In an openshift environment, deploy a persistent jenkins instance using the [jenkins-persistent template]( https://raw.githubusercontent.com/openshift/origin/master/examples/jenkins/jenkins-persistent-template.json). Pass the parameter `ENABLE_OAUTH=false` to disable OAUTH and set the default username and password to admin:password

2. Deploy the builds and secrets in the openshift environment using the `openshift-tools-pr-automation-template.json` in this directory. A username and oauth token for a github user will be required. The user and org whitelists will need to be specified with at least one user or org that will be allowed to run tests.

3. Add the openshift-ops-bot secret to the jenkins deployment to allow the jenkins pipeline access to the bots credentials. The pipeline needs this data to be mounted at /openshift-ops-bot to post the initial "tests pending" status update to pull requests:
```
oc set volumes dc/jenkins --add -t secret --secret-name=openshift-ops-bot-secret -m /openshift-ops-bot
```

4. Log into the jenkins instance using the default credentials. Navigate to 'Manage Jenkins' > 'Manage Users' and click the 'config' icon for the admin user. Change the admin users password to something much more secure.

5. In jenkins, navigate to 'Manage Jenkins' > 'Configure Global Security'. Under 'Access Control' > 'Authorization', the radio button 'Matrix-based security' should be checked by default. In the matrix, select 'Read' access for the Anonymous group under 'Job'. Additionally, select 'Build' for the Anonymous group under 'Job'. This will allow github to post to jenkins via webhooks.

6. Due to a [bug in jenkins](https://issues.jenkins-ci.org/browse/JENKINS-28466), it is necessary to navigate to 'Manage Jenkins' > 'Configure System' and hit 'Save'. If this is not done, certain environment variables, such as `BUILD_URL` will not be available to jenkins pipeline builds.

7. In Jenkins, create a new jenkins pipeline job. Configure the following:
  1. Check the 'This project is parameterized' box and add a 'String Parameter' with the Name 'payload' (case-sensitive). Leave all other boxes empty.
  2. Under 'Build Triggers', check the 'Trigger builds remotely' checkbox and specify any string to use as the authorization token. This same token will be used later to configure the github webhook.
  3. Under 'Pipeline', you can either have jenkins pull the pipeline instructions Jenkinsfile from github, or you can copy and paste the Jenkinsfile contents from `jenkins/test/Jenkinsfile` into the text box. Grabbing the Jenkinsfile from Github will add 10-20 seconds to the build time. Select 'Pipeline script from SCM' as the pipeline definition. Choose 'Git' as the SCM and specify `https://github.com/openshift/openshift-tools` as the repository url. Leave the 'Branches to build' blank. For the 'Script path', set to 'jenkins/Jenkinsfile'
  4. Uncheck the "use groovy sandbox" checkbox. The mounted secret volume cannot be accessed by the pipeline from within the sandbox.
  5. Save the job
    
8. In github, navigate to the settings for openshift-tools with administrator permissions. Under webhooks, create a new webhook and configure the following:
  1. The Payload URL will be the url of the jenkins build trigger configured earlier. Here is an example where 'someuniquestring' is specified as the build trigger token: `https://jenkins-exampleproject.example.com/job/job_name/buildWithParameters?token=someuniquestring`
  2. Set the 'Content type' to `application/x-www-form-urlencoded`. This enabled the webhook payload to be sent as a parameter to the jenkins job.
  3. Under "Which events would you like to trigger", select only 'Pull request'.
  4. Check the 'Active' box to ensure the github webhook is active
  5. Hit 'Update webhook' to save the changes.

9. Ensure that the github user used to update pull requests has push permissions to the repository. As an adiministrator of the repository, navigate to 'Settings' > 'Collaborators' to invite the user to have 'Write' permissions.

## Possible Gotchas
- The `test/run_tests.py` file is the only file that is not dynamically updated with changes. This means that if you modify `test/run_tests.py` in a pull request, those changes will not take affect during testing until the changes have been merged. This occurs because `test/run_tests.py` is the entrypoint to testing that pulls in the changes. Something must run to pull in the changes made in a pull request that will be unaffected by the pull request. The testing currently runs from the 'stg' branch to help with this. Once the commit is merged to stg, the pull request submitting the changes to the prod branch will run with the updated `test/run_tests.py` to allow for proper verification.
- Tests in the `test/Validators/` directory are run dynamically. If a pull request includes a new *.py or *.sh executable script in this directory, it will be run during testing. Because of the possible security implications, there are whitelists that must be used to specify only trusted individuals allowed to run tests.
- To build and install rpms, the testing must run as root. This requires the testing to be run as a docker build. The docker build adds some extra complexity and a good deal of additional time to the testing process. Pull requests will not be updated with an indication that testing is in progress until the `test/run_tests.py` executable has been called during the docker build. This delay can cause some confusion.
