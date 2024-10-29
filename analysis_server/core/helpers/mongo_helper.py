from pymongo import MongoClient, errors


def get_mongo_collection(mongo_url, mongo_database):
    """Connects to MongoDB and ensures that the specified database and collection exist."""
    try:
        # Attempt to connect to the MongoDB client
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)  # 5 seconds timeout
        client.admin.command('ping')  # Check if MongoDB is reachable

        # Access the database
        db = client[mongo_database]

        # Check if the collection exists, create if it doesn't
        if "images" not in db.list_collection_names():
            db.create_collection("images")

        print("Connected to MongoDB and ensured database/collection existence.")
        return db.images

    except errors.ServerSelectionTimeoutError:
        print("MongoDB is not reachable. Exiting the script.")
        exit(1)