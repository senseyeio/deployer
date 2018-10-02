#!/bin/bash
set -euvo pipefail

compose_file=${1:-}
if [[ -z "$compose_file" ]]; then
    echo "usage: $0 <compose_file>"
    exit 1
fi

aws configure set region ${AWS_REGION}
dockerLoginCmd=$(aws ecr get-login --no-include-email)
echo $($dockerLoginCmd)

sed -i -e "s#build: .#image: ${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/prognosys/${SERVICE_NAME}:${BUILD_NO}#g" $1
ecs-cli configure --cluster ${CLUSTER_NAME} --region ${AWS_REGION}
ecs-cli compose -p ${SERVICE_NAME} -f $1 service up --deployment-max-percent 200 --deployment-min-healthy-percent 100
