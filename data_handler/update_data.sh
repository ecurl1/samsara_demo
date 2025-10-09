#!/bin/bash

# Variable dfinitions
IMAGE_NAME="data-handler-demo"
CONTAINER_NAME="data-handler-demo-temp" # Renamed to avoid conflict (Good practice)
TAG="v3"

START_TIME="$1"
END_TIME="$2"
HOST_BASE_DIR="${3:-$(pwd)}"

# Initialize an array for arguments
DOCKER_ARGS_ARRAY=()
if [ -n "$START_TIME" ]; then
    DOCKER_ARGS_ARRAY+=(--start-time "$START_TIME")
fi
if [ -n "$END_TIME" ]; then
    DOCKER_ARGS_ARRAY+=(--end-time "$END_TIME")
fi

# api token configuration
HOST_SECRET_DIR="$HOST_BASE_DIR/data_handler/secrets"
HOST_SECRET_FILE="$HOST_SECRET_DIR/api_token.txt"
CONTAINER_SECRET_FILE=/data_handler/secrets/api_token.txt

cd /data_handler

# Force the shell to find the command and set DOCKER_COMMAND
DOCKER_COMMAND=$(which docker 2> /dev/null)
if [ -z "$DOCKER_COMMAND" ]; then
    # Fallback to standard location if 'which' fails (after apt install)
    if [ -f "/usr/bin/docker" ]; then
        DOCKER_COMMAND="/usr/bin/docker"
    else
        echo "[ERROR] Failed to locate the docker executable. Is docker-client installed in the server container?"
        exit 1
    fi
fi

# Remove old container if present (using the new temp name)
echo "[BUILD] Cleaning up $CONTAINER_NAME (Image: $IMAGE_NAME:$TAG)..."
"$DOCKER_COMMAND" stop $CONTAINER_NAME 2> /dev/null
"$DOCKER_COMMAND" rm $CONTAINER_NAME 2> /dev/null

# Build the docker image
echo "[BUILD] Building new image: $IMAGE_NAME:$TAG"
"$DOCKER_COMMAND" build -t "$IMAGE_NAME:$TAG" .

# Verify build was successful
if [ $? -ne 0 ]; then
    echo "[BUILD] BUILD FAILED: EXITING"
    exit 1
fi

# run the container to execute the data update script
echo "[RUN] Running data handler container $CONTAINER_NAME..."
"$DOCKER_COMMAND" run \
    --rm \
    --name "$CONTAINER_NAME" \
    -v "$HOST_SECRET_FILE:$CONTAINER_SECRET_FILE:ro" \
    -v "$HOST_BASE_DIR/data:/data_handler/data" \
    --entrypoint "python3" \
    "$IMAGE_NAME:$TAG" \
    /data_handler/src/get_data_main.py \
    "${DOCKER_ARGS_ARRAY[@]}"

# cleanup after run finished
echo "[BUILD] Data handler run finished."