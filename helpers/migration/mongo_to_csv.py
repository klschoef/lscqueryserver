import csv
import pandas as pd
import argparse
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_mongo_data(mongo_url, db, collection_name):
    client = MongoClient(mongo_url)
    db = client[db]  # This assumes the database is the default one set in the URI
    collection = db[collection_name]

    data = []
    try:
        filter_query = {"blip2caption": {"$exists": True, "$ne": ""}}
        fields_to_return = {"blip2caption": 1, "filepath": 1, "_id": 0}

        results = collection.find(filter_query, fields_to_return)
        for doc in results:
            description = doc.get("blip2caption")
            data.append({
                "id": doc.get("filepath"),
                "description": description,
            })
        logging.info(f"Total documents fetched: {len(data)}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        client.close()

    return data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    if 'description' in df.columns:
        df['description'] = df['description'].apply(lambda x: x if isinstance(x, str) else None)
    logging.info(f"Storing file '{filename}'...")
    df.to_csv(filename, index=False, columns=['id', 'description'], quoting=csv.QUOTE_ALL, escapechar='\\')
    logging.info(f"Data successfully saved to '{filename}'")

def main():
    parser = argparse.ArgumentParser(description='Fetch data from MongoDB and save it to CSV.')
    parser.add_argument('mongo_url', help='MongoDB connection URI')
    parser.add_argument('db', help='MongoDB database')
    parser.add_argument('collection', help='MongoDB collection name')
    parser.add_argument('output_file', help='Filename for the output CSV')
    args = parser.parse_args()

    logging.info("Starting the data fetch process.")
    mongo_data = fetch_mongo_data(args.mongo_url, args.db, args.collection)
    save_to_csv(mongo_data, args.output_file)

if __name__ == "__main__":
    main()
