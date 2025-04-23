import os

import pandas as pd
import numpy as np
import logging
import faiss
from lsc_shared.clip.core.exceptions.empty_index_exception import EmptyIndexException


def csv_to_faiss(csvfilename, faissfilename, labelfilename):
    logging.info(f'Loading data from {csvfilename}')

    # Check if the CSV file exists and is not empty
    if not os.path.isfile(csvfilename) or os.path.getsize(csvfilename) < 10:
        raise ValueError(f'CSV file {csvfilename} is empty or does not exist')

    # Read the CSV file
    csvdata = pd.read_csv(csvfilename, sep=",", header=None)

    # Extract data (excluding the labels in the first column)
    data = csvdata.iloc[:, 1:].values.astype('float32')
    # Extract labels (from the first column)
    labels = csvdata.iloc[:, 0].tolist()

    logging.info(f'Data loaded with shape {data.shape}')

    # Create the index
    d = data.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(data)  # Add data to the index

    # Save the index
    faiss.write_index(index, faissfilename)
    logging.info(f'Index saved to {faissfilename}')

    # Save labels in a separate file
    with open(labelfilename, 'w') as f:
        for label in labels:
            f.write(f"{label}\n")
    logging.info(f'Labels saved to {labelfilename}')

def get_faiss_and_label_paths(folder_path):
    faiss_file_path = os.path.join(folder_path, "index.faiss")
    labels_file_path = os.path.join(folder_path, "index.labels")

    return faiss_file_path, labels_file_path

def save_faiss_index_with_labels(index, labels, folder_path):
    # Define the file paths for the index and labels within the specified folder
    faiss_file_path, labels_file_path = get_faiss_and_label_paths(folder_path)

    # Save the FAISS index
    faiss.write_index(index, faiss_file_path)
    logging.info(f"Saved FAISS index with {index.ntotal} vectors to {faiss_file_path}")

    # Save the labels
    with open(labels_file_path, 'w') as file:
        for label in labels:
            file.write(f"{label}\n")

    logging.info(f"Saved {len(labels)} labels to {labels_file_path}")

def save_faiss_index(index, folder_path):
    # Define the file paths for the index and labels within the specified folder
    faiss_file_path, labels_file_path = get_faiss_and_label_paths(folder_path)

    # Save the FAISS index
    faiss.write_index(index, faiss_file_path)
    logging.info(f"Saved FAISS index with {index.ntotal} vectors to {faiss_file_path}")

def remove_from_faiss_index(index, label_id):
    id_array = np.array([label_id], dtype='int64')
    index.remove_ids(id_array)

def append_labels_to_label_file(labels, folder_path):
    # Define the file path for the labels within the specified folder
    faiss_file_path, labels_file_path = get_faiss_and_label_paths(folder_path)

    # Append the labels to the existing file
    with open(labels_file_path, 'a') as file:
        for label in labels:
            file.write(f"{label}\n")

    logging.info(f"Appended {len(labels)} labels to {labels_file_path}")

def save_label_file(labels, folder_path):
    # Define the file path for the labels within the specified folder
    faiss_file_path, labels_file_path = get_faiss_and_label_paths(folder_path)

    # Save the labels
    with open(labels_file_path, 'w') as file:
        for label in labels:
            file.write(f"{label}\n")

    logging.info(f"Saved {len(labels)} labels to {labels_file_path}")

def load_clip_features(folder_path, create_if_not_exists=False):
    # Define the file paths for the index and labels within the specified folder
    faiss_file_path, labels_file_path = get_faiss_and_label_paths(folder_path)

    # Load the FAISS index
    if not os.path.isfile(faiss_file_path):

        if create_if_not_exists:
            prepare_folder_and_files(folder_path)
        else:
            raise FileNotFoundError(f"The FAISS index file {faiss_file_path} does not exist")

    index = faiss.read_index(faiss_file_path)
    logging.info(f"Loaded FAISS index with {index.ntotal} vectors")

    # Load the labels
    if not os.path.isfile(labels_file_path):
        raise FileNotFoundError(f"The labels file {labels_file_path} does not exist")

    with open(labels_file_path, 'r') as file:
        labels = file.read().splitlines()

    logging.info(f"Loaded {len(labels)} labels")

    return index, labels

def prepare_folder_and_files(folder_path, index_shape=1024):
    # Define the file paths using the helper function
    faiss_file_path, labels_file_path = get_faiss_and_label_paths(folder_path)

    # Remove existing folder with files if it exists
    if os.path.exists(folder_path):
        for file_path in [faiss_file_path, labels_file_path]:
            if os.path.isfile(file_path):
                os.remove(file_path)
        logging.info(f"Removed existing files in folder at {folder_path}")

    # Remove folder
    if os.path.exists(folder_path):
        os.rmdir(folder_path)
        logging.info(f"Removed existing folder at {folder_path}")

    # Ensure the directory exists
    os.makedirs(folder_path)
    logging.info(f"Created directory at {folder_path}")

    # Create an empty FAISS index and save it as a placeholder
    dimension = index_shape
    index = faiss.IndexFlatL2(dimension)  # Using L2 distance for placeholder
    faiss.write_index(index, faiss_file_path)
    logging.info(f"Created placeholder FAISS index file at {faiss_file_path}")

    # Check if the labels file exists, create it if not
    with open(labels_file_path, 'w') as f:
        f.write("")  # Create an empty file
    logging.info(f"Created empty labels file at {labels_file_path}")

    return faiss_file_path, labels_file_path