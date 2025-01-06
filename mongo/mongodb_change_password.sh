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

# Prompt for the new password and confirm it
echo "Enter new password:"
read -s new_password
echo "Confirm new password:"
read -s confirm_password

if [ "$new_password" != "$confirm_password" ]; then
    echo "Error: Passwords do not match."
    exit 1
fi

# Change the password using mongosh
echo "Changing password for user ${MONGO_USERNAME}."
docker exec -it lsc-mongodb mongosh "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@localhost:27017/admin" --eval "db.changeUserPassword('${MONGO_USERNAME}', '${new_password}');"

if [ $? -eq 0 ]; then
    echo "Password changed successfully."
    # Optionally update the .env file with the new password
    if [[ "$OSTYPE" == "darwin"* ]]; then
      echo "Run Mac SED command"
      sed -i '' "s/MONGO_PASSWORD=${MONGO_PASSWORD}/MONGO_PASSWORD=${new_password}/" ./.env
    else
      echo "Run Linux SED command"
      sed -i "s/MONGO_PASSWORD=${MONGO_PASSWORD}/MONGO_PASSWORD=${new_password}/" ./.env

    fi

    if [ $? -eq 0 ]; then
        echo "Password updated successfully in .env file."
    else
        echo "Failed to update the password in the .env file."
    fi
else
    echo "Error changing password."
fi
