#!/bin/bash

set -e 

REPOSITORY=elastisys/kairosdb
TAG=1.2.1
IMAGE="${REPOSITORY}:${TAG}"

echo "Building Docker image ${IMAGE} ..."
docker build --pull -t ${IMAGE} .

if [ "${PUSH}" == "yes" ]; then
    echo " Pushing Docker image ${IMAGE} ..."
    docker push ${IMAGE}
else
    echo "Docker push disabled by env variable PUSH=${PUSH}"
fi

echo "Build of ${IMAGE} finished"
