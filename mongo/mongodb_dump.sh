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

# Check if a specific database name is provided
if [ "$1" ]; then
    db_name="--db $1"
    echo "Backing up specific database: $1"
else
    db_name=""
    echo "Backing up all databases."
fi

# Create a backup
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
backup_file="dump_${timestamp}.gz"

docker exec lsc-mongodb mongodump --archive --gzip --username ${MONGO_USERNAME} --password ${MONGO_PASSWORD} --authenticationDatabase admin $db_name > ./backups/$backup_file

if [ $? -eq 0 ]; then
    echo "Backup was successfully created: $backup_file"
else
    echo "Error creating backup."
fi