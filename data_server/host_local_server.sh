#!/bin/bash

# some configuration - make sure docker is on path, define image and 
cd /home/ecurl/samsara_demo/data_server
export PATH="/snap/bin:$PATH"
IMAGE_NAME="data-server-demo"
CONTAINER_NAME="data-server-demo"
TAG="v0"

# remove old container if present
echo "[BUILD] Cleaning up $CONTAINER_NAME..."
docker stop $CONTAINER_NAME 2> /dev/null
docker rm $CONTAINER_NAME 2> /dev/null

# build the docker image
echo "[BUILD] Building new image: $CONTAINER_NAME:$TAG"
docker build -t "$IMAGE_NAME:$TAG" .

# verify build was succesful - print out build error if not
if [ $? -ne 0 ]; then
    echo "[BUILD] BUILD FAILED: EXITING"
    exit 1
fi

# run the docker - main scripts here, defined in Dockerfile
docker run \
    -d \
    -p 8080:5000 \
    --name "$CONTAINER_NAME" \
    -v /home/ecurl/samsara_demo/data:/data_server/data \
    "$IMAGE_NAME:$TAG" \

# cleanup after run finished
echo "[BUILD] Container build finished"

