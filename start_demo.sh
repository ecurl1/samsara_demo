#!/bin/bash

# some configuration - make sure docker is on path, define image and 
export PATH="/snap/bin:$PATH"
IMAGE_NAME="sensor-demo"
CONTAINER_NAME="samsara-demo"
TAG="v0"

# api token configuration - /secrets is ignored by docker and git, only available locally
HOST_SECRET_DIR=$(pwd)/secrets
HOST_SECRET_FILE=$HOST_SECRET_DIR/api_token.txt
CONTAINER_SECRET_FILE=/app/run/api_token.txt

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
    --name "$CONTAINER_NAME" \
    -v "$HOST_SECRET_FILE:$CONTAINER_SECRET_FILE:ro" \
    "$IMAGE_NAME:$TAG"

# cleanup after run finished
echo "[BUILD] Container finished, removing instance $CONTAINER_NAME..."
docker rm $CONTAINER_NAME

