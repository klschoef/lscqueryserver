import os
import pandas as pd
import logging
import faiss

from core.exceptions.empty_index_exception import EmptyIndexException

logging.basicConfig(level=logging.DEBUG)

def loadClipFeatures(csvfilename):
    logging.info(f'loading features from {csvfilename}')

    # check if csv is empty
    if not os.path.isfile(csvfilename) or os.path.getsize(csvfilename) < 10:
        raise EmptyIndexException(f'CSV file {csvfilename} is empty')

    # read csv
    csvdata = pd.read_csv(csvfilename, sep=",", skiprows=0, header=None)

    # extract data (without the labels in the first column)
    data = csvdata.iloc[0:,1:]
    # extract labels (from the first column)
    datalabels = csvdata.iloc[0:, 0]

    logging.info(f"loaded data: {data.info}")

    d = data.shape[1]
    #index = faiss.IndexFlatL2(d)   # build the index (L2 distance)
    index = faiss.IndexFlatIP(d)   # build the index with inner product (cosine similarity)
    index.add(data)
    logging.info(index.ntotal)
    logging.info(index.is_trained)

    return index, data, datalabels