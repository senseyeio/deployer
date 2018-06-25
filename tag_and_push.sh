#!/bin/bash
set -euv pipefail

docker-compose -p=repo build
docker tag repo_${SERVICE_NAME}:latest ${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/prognosys/${SERVICE_NAME}:${BUILD_NO}
docker push "${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/prognosys/${SERVICE_NAME}:${BUILD_NO}"
