import argparse
import requests
import pymongo
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def import_to_solr(base_url, core_name, data):
    """Import data into the Solr core."""
    solr_url = urljoin(base_url+"/", f"{core_name}/update/json/docs?commit=true")
    headers = {'Content-type': 'application/json'}
    response = requests.post(solr_url, json=data, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to import data to Solr: {response.text}")
        raise Exception(f"Failed to import data to Solr: {response.text}")
    logging.info("Data imported to Solr successfully.")

def fetch_from_mongo(mongo_uri, db_name, collection_name, query, fields):
    """Fetch data from MongoDB."""
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    documents = list(collection.find(query, fields))
    logging.info(f"Fetched {len(documents)} documents from MongoDB.")
    return documents

def main():
    parser = argparse.ArgumentParser(description='Import descriptions from MongoDB to a Solr core.')
    parser.add_argument('--mongo_uri', required=True, help='MongoDB URI')
    parser.add_argument('--db_name', required=True, help='MongoDB database name')
    parser.add_argument('--collection_name', required=True, help='MongoDB collection name')
    parser.add_argument('--solr_url', required=True, help='Solr base URL')
    parser.add_argument('--solr_core', required=True, help='Solr core name')
    args = parser.parse_args()

    # MongoDB query and fields
    filter_query = {"blip2caption": {"$exists": True, "$ne": ""}}
    fields_to_return = {"blip2caption": 1, "filepath": 1, "_id": 0}

    # Fetch data from MongoDB
    documents = fetch_from_mongo(args.mongo_uri, args.db_name, args.collection_name, filter_query, fields_to_return)

    # Prepare data for Solr
    solr_data = [
        {"id": doc["filepath"], "description": doc["blip2caption"]}
        for doc in documents
    ]

    # Import data into Solr
    import_to_solr(args.solr_url, args.solr_core, solr_data)

if __name__ == "__main__":
    main()
