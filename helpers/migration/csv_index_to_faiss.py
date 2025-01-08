import argparse
import logging
import os
from lsc_shared.clip.core.helpers.faiss_helper import csv_to_faiss

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert CSV file to FAISS index and save labels in a specified folder.")
    parser.add_argument("csv_filename", type=str, help="Path to the CSV file containing the data.")
    parser.add_argument("-f", "--foldername", type=str, help="Folder name to save the FAISS index and labels, defaults to CSV filename with .faiss extension.")

    args = parser.parse_args()

    # Determine the output folder
    if args.foldername:
        output_folder = args.foldername
    else:
        # Default folder name is the CSV file name with .faiss extension
        output_folder = args.csv_filename.replace(".csv", ".faiss")

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Paths for the FAISS index and labels
    faiss_filename = os.path.join(output_folder, "index.faiss")
    label_filename = os.path.join(output_folder, "index.labels")

    # Load data, create FAISS index, and save the index and labels
    try:
        csv_to_faiss(args.csv_filename, faiss_filename, label_filename)
        logging.info(f"Successfully processed the CSV file and updated the FAISS index and labels in {output_folder}.")
    except Exception as e:
        logging.error(f"Failed to process the CSV file: {e}")

if __name__ == "__main__":
    main()
