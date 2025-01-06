#!/bin/bash

# Define the path to your docker-compose file
DOCKER_COMPOSE_PATH="./"  # Adjust this path as necessary

# Load environment variables
if [ -f "${DOCKER_COMPOSE_PATH}/.env" ]; then
    export $(cat "${DOCKER_COMPOSE_PATH}/.env" | grep -v '^#' | awk '/=/ {print $1}')
else
    echo "Error: .env file not found in ${DOCKER_COMPOSE_PATH}."
    exit 1
fi

# Stop and remove all containers and volumes
echo "Stopping all containers and removing volumes..."
docker-compose -f "${DOCKER_COMPOSE_PATH}/docker-compose.yml" down -v
rm -rf mongodb_data

# Recreate and start the container
echo "Recreating MongoDB container and starting it..."
docker-compose -f "${DOCKER_COMPOSE_PATH}/docker-compose.yml" up -d

if [ $? -eq 0 ]; then
    echo "MongoDB container recreated and started successfully."
else
    echo "Error recreating and starting MongoDB container."
fi
