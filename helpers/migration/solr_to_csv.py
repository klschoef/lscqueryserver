import csv

import requests
import pandas as pd
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_solr_data(base_url, core, params, rows=1000):
    data = []
    start = 0
    total = None

    while total is None or start < total:
        query_params = params.copy()
        query_params.update({
            'start': start,
            'rows': rows,
        })
        response = requests.get(f"{base_url}/{core}/select", params=query_params)
        response_json = response.json()

        if total is None:
            total = response_json['response']['numFound']
            logging.info(f"Total documents found: {total}")

        docs = response_json['response']['docs']
        data.extend(docs)
        start += len(docs)

        logging.info(f"Fetched {len(docs)} documents, starting at document {start}")

    return data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df['description'] = df['description'].apply(lambda x: x[0] if x and isinstance(x, list) else None)
    logging.info(f"Store file '{filename}' ...")
    df.to_csv(filename, index=False, columns=['id', 'description'])
    logging.info(f"Data successfully saved to '{filename}'")

def main():
    parser = argparse.ArgumentParser(description='Fetch data from Solr and save it to CSV.')
    parser.add_argument('solr_url', help='Base URL of the Solr server')
    parser.add_argument('core', help='Name of the Solr core')
    parser.add_argument('output_file', help='Filename for the output CSV')
    args = parser.parse_args()

    logging.info("Starting the data fetch process.")
    params = {
        'q': '*:*',
        'indent': 'true',
        'q.op': 'OR',
    }

    solr_data = fetch_solr_data(args.solr_url, args.core, params)
    save_to_csv(solr_data, args.output_file)

if __name__ == "__main__":
    main()
