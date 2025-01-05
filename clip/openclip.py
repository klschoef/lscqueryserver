import argparse
import io
import sys
from pathlib import Path

from PIL import Image
import open_clip
import faiss
import torch
import asyncio
import websockets
import json
import pandas as pd
import csv
import numpy as np
import os
from websockets.exceptions import ConnectionClosedOK
import requests
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.DEBUG)
import psutil
memory = psutil.virtual_memory()
logging.info(f"Available Memory: {memory.available / (1024 ** 3):.2f} GB")

dotenv_path = os.path.join(os.path.dirname(__file__), 'clip.env')
load_dotenv(dotenv_path)

# Parse command-line arguments
# TODO: add default values to env variables
parser = argparse.ArgumentParser(description="OpenCLIP Search Server")
parser.add_argument('--keyframe_base_root', default=os.getenv("keyframe_base_root", "/images"), help='Base path to the images (keyframes)')
parser.add_argument('--csv_file', default=os.getenv("csv_file", "/faiss_index.csv"), help='Path to the CSV file')
parser.add_argument('--ws_port', default=int(os.getenv("faiss_ws_port", "8002")), help='Websocket Port')
parser.add_argument('--image_server_path', default=os.getenv("faiss_image_server_path", "http://extreme00.itec.aau.at/lifexplore"), help='Base path to the image server')
parser.add_argument('--image_server_timeout', default=int(os.getenv("faiss_image_server_timeout", "5")), help='Timeout for image server requests')
parser.add_argument('--model_name', default=os.getenv("model_name", "ViT-H-14"), help='Model Name')
parser.add_argument('--weights_name', default=os.getenv("weights_name", "laion2b_s32b_b79k"), help='Weights Name')

args = parser.parse_args()
keyframe_base_root = args.keyframe_base_root
csv_file = args.csv_file
ws_port = args.ws_port
image_server_path = args.image_server_path
image_server_timeout = args.image_server_timeout
logging.info(f"try to start on port {ws_port} with image_server_path {image_server_path} ...")
logging.info(f"csv_file: {csv_file}")

clipdata = []
index, labels = None, None
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(device)
model, _, preprocess = open_clip.create_model_and_transforms(args.model_name, pretrained=args.weights_name, device=device)
logging.info('model loaded')

csvfile = open(args.csv_file, 'a')
csvwriter = csv.writer(csvfile, delimiter=',')

def main():
    global index, labels
    index, labels = loadClipFeatures('lsc', csv_file)
    asyncio.run(run_ws())

def search(text_features, k):
    D, I = index.search(text_features, k)
    return D, I

def similaritysearch(idx, k):
    D, I = index.search(clipdata[0][idx:idx+1], k)
    return D, I

def getLabels():
    return labels

def filterAndLabelResults(I, D, resultsPerPage, selectedPage):
    labels = getLabels()
    kfresults = []
    kfresultsidx = []
    kfscores = []
    ifrom = (selectedPage - 1) * resultsPerPage
    ito = selectedPage * resultsPerPage
    #for idx in I[0]:
    logging.info(f'from:{ifrom} to:{ito}')
    for i in range(ifrom,ito):
        idx = I[0][i]
        score = D[0][i]
        if idx == -1:
            logging.info(f"idx: {idx}, score: {score}, i: {i}")
            break
        kfresults.append(str(labels[idx]))
        kfresultsidx.append(int(idx))
        kfscores.append(str(score))
    return kfresults, kfresultsidx, kfscores

async def handler(websocket):
    try:
        while True:
            message = await websocket.recv()
            logging.info(message)
            event = json.loads(message).get('content', {})
            clientId = event.get('clientId')

            if 'ping' not in event:

                #logging.info(event['query'])

                with torch.no_grad():
                    D = []
                    I = []
                    k = int(event.get('maxresults', '0'))
                    resultsPerPage = int(event.get('resultsperpage', '0'))
                    selectedPage = int(event.get('selectedpage', '1'))
                    event_type = event.get('type', 'textquery')
                    #image_features = model.encode_image(image)

                    if event['type'] == 'textquery':
                        input = open_clip.tokenize(event['query']).to(device)
                        logging.info(input.shape)
                        text_features = model.encode_text(input).cpu()
                        logging.info(text_features.shape)
                        D, I = search(text_features, k)
                    elif event_type == 'indexrequest':
                        filepath = event.get('filepath')
                        img_path = os.path.join(keyframe_base_root, filepath)
                        logging.info(f'try to load {img_path} ...')
                        if Path(img_path).exists():
                            image = Image.open(img_path)
                        else:
                            await websocket.send(json.dumps({'error': f'file {img_path} not found'}))
                            return

                        image = preprocess(image).unsqueeze(0).to(device)
                        image_features = model.encode_image(image)
                        image_features = image_features.cpu()
                        logging.info('shape:',image_features.shape)
                        features_list = image_features[0].tolist()
                        logging.info('features extracted')

                        logging.info('writing to csv')
                        features_list.insert(0, filepath)
                        csvwriter.writerow(mylist)

                        logging.info('reload local index')
                        loadClipFeatures('lsc', csv_file)

                        logging.info('return features to client')
                        tmp = json.dumps({'filepath': filepath, 'added_entry': features_list})
                        await websocket.send(tmp)
                        return
                    elif event['type'] == 'similarity-query':
                        D, I = similaritysearch(int(event['query']), k)
                    elif event['type'] == 'file-similarityquery':
                        logging.info(f'trying to load {event["query"]} from {keyframe_base_root} {event["pathprefix"]}')
                        # check if path is on local machine
                        img_path = os.path.join(keyframe_base_root,event['pathprefix'],event['query'])
                        logging.info(f'try to load {img_path} ...')
                        if Path(img_path).exists():
                            image = Image.open(img_path)
                        else:
                            logging.info(f'{img_path} does not exist, trying to load from remote server ...')
                            path_parts = [part.strip("/") for part in [image_server_path,event["pathprefix"],event["query"]] if len(part) > 0]
                            img_path = "/".join(path_parts)
                            logging.info(f'trying to load from remote {img_path} ...')
                            response = requests.get(str(img_path), timeout=image_server_timeout)
                            if response.ok:
                                image_data = response.content
                                image = Image.open(io.BytesIO(image_data))
                                logging.info(f'loaded {img_path}')

                        if not image:
                            logging.info(f'could not load {img_path}')
                            continue
                        image = preprocess(image).unsqueeze(0).to(device)
                        image_features = model.encode_image(image)
                        image_features = image_features.cpu()
                        logging.info('shape:',image_features.shape)
                        mylist = image_features[0].tolist()
                        logging.info('features extracted')
                        D, I = search(image_features, k)
                        logging.info('file-similarity search finished')

                    kfresults, kfresultsidx, kfscores = filterAndLabelResults(I, D, resultsPerPage, selectedPage)
                    results = {'num':len(kfresults), 'clientId':clientId, 'totalresults':k, 'results':kfresults, 'resultsidx':kfresultsidx, 'scores':kfscores }
                    tmp = json.dumps(results)
                    #logging.info(tmp)
                    await websocket.send(tmp)
    except ConnectionClosedOK:
        logging.info("Connection closed gracefully.")
    except Exception as e:
        logging.info("Exception: ", str(e))


async def run_ws():
    async with websockets.serve(handler, "", ws_port):
        logging.info(f'listening on {ws_port}')
        await asyncio.Future()  # run forever


def loadClipFeatures(infoname, csvfilename):
    logging.info(f'loading {infoname}: {csvfilename}')
    #data = pd.read_csv(csvfilename, sep=",", index_col=0, skiprows=0, header=None)
    csvdata = pd.read_csv(csvfilename, sep=",", skiprows=0, header=None)
    data = csvdata.iloc[0:,1:]
    datalabels = csvdata.iloc[0:,0]
    clipdata = []
    clipdata.append(data)
    logging.info(data.info)
    #logging.info(datalabels)

    d = 1024 # TODO:  count , from the header line directly via python
    #index = faiss.IndexFlatL2(d)   # build the index (L2 distance)
    index = faiss.IndexFlatIP(d)   # build the index with inner product (cosine similarity)
    index.add(data)
    logging.info(index.ntotal)
    logging.info(index.is_trained)

    return index, datalabels

main()

