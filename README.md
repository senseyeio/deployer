## Deployment Docker Image

To keep our deployment process as CI-agnostic as possible, and to speed deployment times via caching, this deployment docker image contains the necessary scripts needed to deploy a service. Currently this is for AWS, but again this can change as needed. 

CircleCI references this image in its config.yml file (see circleci/config.yml). This can be seen as the current 'pristine' version of the config file, which will be used when new services are made.

If this Docker image changes, CircleCI can be updated by changing the DEPLOYER_IMAGE environmental variable (see below). If the circleci/config.yml file changes, all services should be updated - so this is ideally a rare thing.

### Environment Variables

Two variables need to be provided by the service config. The rest come from the CI:

- CLUSTER_NAME: Which cluster to deploy the service onto
- SERVICE_NAME: e.g. `test-service`

The CI should be configured to have:
- AWS_REGION: e.g. eu-west-1
- AWS_ACCOUNT: the AWS account ID

And at build-time the CI should provide:
- BUILD_NO: currently the SHA of the commit that triggered the build. Note that this is different from the build number used previously (CircleCI treats each step in the workflow as a build, so build numbers aren't sequential).

### Contents of the image

There are 3 scripts included with this image:
* create_repo.sh: creates the service's repository on ECR
* tag_and_push.sh: tags the image in docker and pushes it to ECR
* deploy_image.sh: modifies the service's docker-compose.yml file to use the ECR image; switches to the correct cluster and region; and starts up the image with docker-compose.

These scripts are such that the circleci yml file should not need to change if we switch to other technologies in the future.
