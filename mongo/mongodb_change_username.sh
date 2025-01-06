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

# Check if a new username is provided as an argument
if [ "$1" ]; then
    new_username="$1"
    echo "New username provided via command line: $new_username"
else
    # Prompt for the new username
    echo "Enter new username:"
    read new_username
fi

# Remove the old user and create a new one using mongosh
echo "Removing old user ${MONGO_USERNAME} and creating new user $new_username."
docker exec -it lsc-mongodb mongosh "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@localhost:27017/admin" --eval "
db.createUser({
    user: '$new_username',
    pwd: '${MONGO_PASSWORD}',
    roles: [
        { role: 'root', db: 'admin' } // Adjust the roles as necessary
    ]
});
db.dropUser('${MONGO_USERNAME}');"

if [ $? -eq 0 ]; then
    echo "Username changed successfully."
    # Optionally update the .env file with the new username
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed_cmd="sed -i ''"
    else
        sed_cmd="sed -i"
    fi
    $sed_cmd "s/MONGO_USERNAME=${MONGO_USERNAME}/MONGO_USERNAME=${new_username}/" ./.env

    if [ $? -eq 0 ]; then
        echo "Username updated successfully in .env file."
    else
        echo "Failed to update the username in the .env file."
    fi
else
    echo "Error changing username."
fi
