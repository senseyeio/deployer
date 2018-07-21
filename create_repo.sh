#!/bin/bash
set -euvo pipefail

aws configure set region ${AWS_REGION_ECR}
dockerLoginCmd=$(aws ecr get-login --no-include-email)
echo $($dockerLoginCmd)
~/create_repo.py prognosys/${SERVICE_NAME}
