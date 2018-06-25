#!/bin/bash
set -euv pipefail

aws configure set region ${AWS_REGION}
dockerLoginCmd=$(aws ecr get-login --no-include-email)
echo $($dockerLoginCmd)
aws ecr create-repository --repository-name prognosys/${SERVICE_NAME} || true
