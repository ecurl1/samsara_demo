#!/bin/bash

# --- Input Handling ---
START_TIME="$1" # Quote the inputs right away
END_TIME="$2"   # Quote the inputs right away

# Construct the arguments string for the docker run command
# Initialize an array for arguments
DOCKER_ARGS_ARRAY=()

# Append arguments to the array
if [ -n "$START_TIME" ]; then
    DOCKER_ARGS_ARRAY+=(--start-time "$START_TIME")
fi
if [ -n "$END_TIME" ]; then
    DOCKER_ARGS_ARRAY+=(--end-time "$END_TIME")
fi
# ----------------------

# some configuration - make sure docker is on path, define image and 
cd /home/ecurl/samsara_demo/data_handler
export PATH="/snap/bin:$PATH"
IMAGE_NAME="data-handler-demo"
CONTAINER_NAME="data-handler-demo"
TAG="v3"

# api token configuration - /secrets is ignored by docker and git, only available locally
HOST_SECRET_DIR=$(pwd)/secrets
HOST_SECRET_FILE=$HOST_SECRET_DIR/api_token.txt
CONTAINER_SECRET_FILE=/data_handler/secrets/api_token.txt

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
    -v /home/ecurl/samsara_demo/data:/data_handler/data \
    --entrypoint "python3" \
    "$IMAGE_NAME:$TAG" \
    /data_handler/src/get_data_main.py \
    "${DOCKER_ARGS_ARRAY[@]}"

# cleanup after run finished
echo "[BUILD] Container finished, removing instance $CONTAINER_NAME..."
docker rm $CONTAINER_NAME