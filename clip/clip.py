import io

import math

import csv

import json

import argparse
import asyncio
import open_clip
import requests
import torch
import websockets
import os
from websockets.exceptions import ConnectionClosedOK
from dotenv import load_dotenv
import logging
from pathlib import Path
from PIL import Image

from core.clip_context import ClipContext
from core.index_context import IndexContext

logging.basicConfig(level=logging.DEBUG)
import psutil
memory = psutil.virtual_memory()
logging.info(f"Available Memory: {memory.available / (1024 ** 3):.2f} GB")

dotenv_path = os.path.join(os.path.dirname(__file__), 'clip.env')
load_dotenv(dotenv_path)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="OpenCLIP Search Server")
parser.add_argument('--keyframe_base_root', default=os.getenv("KEYFRAME_BASE_ROOT", "/images"), help='Base path to the images (keyframes)')
parser.add_argument('--csv_file', default=os.getenv("CSV_FILE", "/faiss_index.csv"), help='Path to the CSV file')
parser.add_argument('--ws_port', default=int(os.getenv("FAISS_WS_PORT", "8002")), help='Websocket Port')
parser.add_argument('--image_server_path', default=os.getenv("FAISS_IMAGE_SERVER_PATH", "http://extreme00.itec.aau.at/lifexplore"), help='Base path to the image server')
parser.add_argument('--image_server_timeout', default=int(os.getenv("FAISS_IMAGE_SERVER_TIMEOUT", "5")), help='Timeout for image server requests')
parser.add_argument('--model_name', default=os.getenv("MODEL_NAME", "ViT-H-14"), help='Model Name')
parser.add_argument('--weights_name', default=os.getenv("WEIGHTS_NAME", "laion2b_s32b_b79k"), help='Weights Name')
args = parser.parse_args()

logging.info(f"try to load csv_file: {args.csv_file}")
index_context = IndexContext(args.csv_file)

clip_context = ClipContext(args.model_name, args.weights_name)
csvfile = open(args.csv_file, 'a')
csvwriter = csv.writer(csvfile, delimiter=',')

def main():
    logging.info(f"try to start on port {args.ws_port} with image_server_path {args.image_server_path} ...")
    asyncio.run(run_ws(args.ws_port))


class EmptyIndexError:
    pass


async def ws_handler(websocket):
    try:
        while True:
            message = await websocket.recv()
            logging.info(message)
            event = json.loads(message).get('content', {})
            D = []
            I = []
            k = int(event.get('maxresults', '0'))
            resultsPerPage = int(event.get('resultsperpage', '0'))
            selectedPage = int(event.get('selectedpage', '1'))
            clientId = event.get('clientId')

            with torch.no_grad():
                event_type = event.get('type', 'textquery')
                if event_type == 'indexrequest':
                    filepath = event.get('filepath')
                    img_path = os.path.join(args.keyframe_base_root, filepath)
                    logging.info(f'try to load {img_path} ...')
                    labels = index_context.get_datalabels()
                    if labels is not None and index_context.get_datalabels().str.contains(filepath).any():
                        await websocket.send(json.dumps({'error': f'file {img_path} already indexed'}))
                        return

                    if Path(img_path).exists():
                        image = Image.open(img_path)
                    else:
                        await websocket.send(json.dumps({'error': f'file {img_path} not found'}))
                        return

                    image = clip_context.preprocess(image).unsqueeze(0).to(clip_context.device)
                    image_features = clip_context.model.encode_image(image)
                    image_features = image_features.cpu()
                    features_list = image_features[0].tolist()
                    logging.info('features extracted')

                    logging.info('writing to csv')
                    features_list.insert(0, filepath)
                    csvwriter.writerow(features_list)

                    logging.info('reload local index')
                    index_context.load_clip_features()

                    # fetch index
                    indicies = index_context.get_datalabels()[index_context.get_datalabels().str.contains(filepath)].index.tolist()
                    if len(indicies) == 0:
                        await websocket.send(json.dumps({'error': 'an error occured, the file is not in the index after adding it!'}))
                        return

                    l2_to_last_one = None
                    added_line_row = indicies[0]
                    if added_line_row > 0:
                        added_entry_index_list = index_context.get_index().reconstruct(added_line_row).tolist()
                        last_entry_index_list = index_context.get_index().reconstruct(added_line_row-1).tolist()

                        # calculate l2 distance to last one
                        l2_to_last_one = calculate_l2_distance(added_entry_index_list, last_entry_index_list)

                    logging.info('return features to client')
                    tmp = json.dumps({
                        'filepath': filepath,
                        'clip_entry_metadata': {
                            'model_name': args.model_name,
                            'weights_name': args.weights_name,
                            'clip_type': 'open_clip',
                            'l2_to_last_one': l2_to_last_one,
                            'added_line_row': added_line_row,
                        }
                    })
                    await websocket.send(tmp)
                    return
                elif event['type'] == 'textquery':
                    input = open_clip.tokenize(event['query']).to(clip_context.device)
                    logging.info(input.shape)
                    text_features = clip_context.model.encode_text(input).cpu()
                    logging.info(text_features.shape)
                    try:
                        D, I = search(text_features, k)
                    except EmptyIndexError:
                        await websocket.send(json.dumps({'error': 'index is empty'}))
                        return
                elif event['type'] == 'similarity-query':
                    D, I = similaritysearch(int(evet['query']), k)
                elif event['type'] == 'file-similarityquery':
                    logging.info(f'trying to load {event["query"]} from {args.keyframe_base_root} {event["pathprefix"]}')
                    # check if path is on local machine
                    img_path = os.path.join(args.keyframe_base_root,event['pathprefix'],event['query'])
                    logging.info(f'try to load {img_path} ...')
                    if Path(img_path).exists():
                        image = Image.open(img_path)
                    else:
                        logging.info(f'{img_path} does not exist, trying to load from remote server ...')
                        path_parts = [part.strip("/") for part in [args.image_server_path,event["pathprefix"],event["query"]] if len(part) > 0]
                        img_path = "/".join(path_parts)
                        logging.info(f'trying to load from remote {img_path} ...')
                        response = requests.get(str(img_path), timeout=args.image_server_timeout)
                        if response.ok:
                            image_data = response.content
                            image = Image.open(io.BytesIO(image_data))
                            logging.info(f'loaded {img_path}')

                    if not image:
                        logging.info(f'could not load {img_path}')
                        continue
                    image = clip_context.preprocess(image).unsqueeze(0).to(clip_context.device)
                    image_features = clip_context.model.encode_image(image)
                    image_features = image_features.cpu()
                    logging.info('shape:',image_features.shape)
                    mylist = image_features[0].tolist()
                    logging.info('features extracted')
                    D, I = search(image_features, k)
                    logging.info('file-similarity search finished')

            kfresults, kfresultsidx, kfscores = filterAndLabelResults(I, D, resultsPerPage, selectedPage)
            results = {'num':len(kfresults), 'clientId': clientId, 'totalresults':k, 'results':kfresults, 'resultsidx':kfresultsidx, 'scores':kfscores }
            tmp = json.dumps(results)
            #logging.info(tmp)
            await websocket.send(tmp)
    except ConnectionClosedOK:
        logging.info("Connection closed gracefully.")
    except Exception as e:
        logging.info("Exception: ", str(e))

def calculate_l2_distance(list1, list2):
    """Calculate the L2 distance between two lists of floats."""
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length.")

    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(list1, list2)))
    return distance


def search(text_features, k):
    D, I = index_context.get_index().search(text_features, k)
    return D, I

def similaritysearch(idx, k):
    D, I = index_context.get_index().search(index_context.get_data()[idx:idx+1], k)
    return D, I

def filterAndLabelResults(I, D, resultsPerPage, selectedPage):
    labels = index_context.get_datalabels()
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

async def run_ws(ws_port):
    async with websockets.serve(ws_handler, "", ws_port):
        logging.info(f'listening on {ws_port}')
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    main()
