#!/bin/bash

# Load environment variables
if [ -f ./.env ]; then
    export $(cat ./.env | grep -v '^#' | awk '/=/ {print $1}')
else
    echo "Error: .env file not found."
    exit 1
fi

# Check if the MongoDB Docker container is running
if [ $(docker ps -q -f name=lsc-mongodb) ]; then
    echo "MongoDB container is running."
else
    echo "Error: MongoDB container is not running."
    exit 1
fi

# Check if a specific backup file is provided
if [ "$1" ]; then
    backup_file="./backups/$1"
    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found."
        exit 1
    fi
    echo "Restoring from specific backup file: $1"
else
    echo "Error: No backup file specified."
    exit 1
fi

# Restore the database
docker exec -i lsc-mongodb mongorestore --archive --gzip --username ${MONGO_USERNAME} --password ${MONGO_PASSWORD} --authenticationDatabase admin < $backup_file

if [ $? -eq 0 ]; then
    echo "Database was successfully restored from: $1"
else
    echo "Error restoring database."
fi