#!/bin/bash
set -euv pipefail

aws configure set region ${AWS_REGION}
dockerLoginCmd=$(aws ecr get-login --no-include-email)
echo $($dockerLoginCmd)

sed -i -e "s#build: .#image: ${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/prognosys/${SERVICE_NAME}:${BUILD_NO}#g" docker-compose.yml
ecs-cli configure --cluster ${CLUSTER_NAME} --region ${AWS_REGION}
ecs-cli compose -p ${SERVICE_NAME} service up
