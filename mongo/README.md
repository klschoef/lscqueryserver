# LSC Mongo DB

## Description

## Setup
```bash
# create certificates for the docker image
./create-certs.sh
# copy and edit the .env file
cp .env.example .env
# CHANGE THE .env FILE TO YOUR NEEDS (ESPECIALLY THE PASSWORDS)
# For development setup
docker-compose up -d
# For production setup (Don't use mongo-express in production with the given configuration)
docker-compose up -d mongo
```

## Usage

### Load Backup
To execute the scripts, make sure that mongo is currently running.
```bash
# copy the backup file to the backups folder. This folder is mapped to the mongo container
cp /path/to/backup/file.gz ./backups/
# restore the backup
./mongodb_restore.sh backups/file.gz
```

### Create Backup
```bash
# create a backup. The backup file is stored in the backups folder with a timestamp
./mongodb_dump.sh
```

### Change Password or username
The password and the username will be also changed in the .env file, so no adjustements are needed.
Make sure, you also change the password and username in the other modules of LSC, where the mongodb is used.
```bash
# change the password for the user
./mongodb_change_password.sh
# change the username for the user (if you don't specify a username, you will get a prompt to enter one)
./mongodb_change_username.sh new_username
# restart to make the changes take effect also on mongo-express
docker-compose down && docker-compose up -d
```

### Reset the database
```bash
# reset the database. This will delete all data in the database
./mongodb_ATTENTION_reset.sh
```