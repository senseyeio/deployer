#!/bin/bash
set -euvo pipefail

aws configure set region ${AWS_REGION_ECR}
dockerLoginCmd=$(aws ecr get-login --no-include-email)
echo $($dockerLoginCmd)

docker tag ${SERVICE_NAME} ${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/prognosys/${SERVICE_NAME}:${BUILD_NO}
docker push "${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/prognosys/${SERVICE_NAME}:${BUILD_NO}"
