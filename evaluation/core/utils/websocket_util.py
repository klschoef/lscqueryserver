import json
import logging
import time

import math

import websockets


async def send_and_receive_raw_message(message, url):
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(message))
        while True:
            response = await ws.recv()
            logging.info(f"Received from {url}: {response}")
            response_json = json.loads(response)
            if response_json.get("type", "") == "progress":
                logging.info(f"Progress from {url}: {response_json.get('message', '')}")
            elif response_json.get("type", "") == "error":
                logging.error(f"Error: {response_json.get('error', '')}")
                exit(1)
            else:
                return json.loads(response)


async def send_and_receive_message(lsc_json, uri, faiss):
    print(f"try to connect to server {uri} ...")
    async with websockets.connect(uri) as websocket:
        print(f"connected to server {uri} ...")
        results = []
        max_results = 100
        for topic_dict in lsc_json:
            print(f"start evaluation for {topic_dict['query_name']} ...")

            result_dict = {
                'query_name': topic_dict['query_name'],
                'recall_per_hint': [],
                'ranks_per_hint': [],
                'debug_info': []
            }
            try:
                for hint in topic_dict.get('hints', []):
                    response = {}
                    while True:
                        request = ({
                            "source": "appcomponent",
                            "content": {
                                "type": "textquery",
                                "clientId": "direct",
                                "selectedpage": 1,
                                "resultsperpage": 1000,
                                "useGPTasDefault": False,
                                "returnCLIPConfig": True,
                                "version": 2,
                                "query": hint,
                                "activate_caching": False,
                                "queryMode": "All Images"
                            }
                        })

                        print(f"send request for: {hint}")

                        await websocket.send(json.dumps(request))
                        error = False
                        while True:
                            response = await websocket.recv()
                            response = json.loads(response)
                            if "results" in response:
                                break
                            elif response.get("type", "") == "progress":
                                print(f"Progress: {response.get('message', '')}")
                            if response.get("type", "") == "error":
                                print(f"Error sending request: {response.get('error', '')}")
                                error = True
                                break

                        if error:
                            logging.error(f"Retry after Error (wait 2 seconds): {response.get('error', '')}")
                            time.sleep(2)
                            continue

                        # check if the clip config is correct, otherwise change it and retry
                        clip_config = response.get("debug_info", {}).get("clip_config", {})
                        faiss_folder = clip_config.get("faiss_folder")
                        model_name = clip_config.get("model_name")
                        weights_name = clip_config.get("weights_name")

                        if not hint.startswith("-") and (faiss_folder != faiss.path or model_name != faiss.model or weights_name != faiss.weights):

                            logging.info(f"switch to faiss index {faiss.path} ...")
                            logging.info(f"load faiss index {faiss.path} (This can take minutes to hours depending on CLIP server's internet connection, and cache state) ...")

                            result = await send_and_receive_raw_message({
                                "source": "appcomponent",
                                "content": {
                                    "type": "change_faiss",
                                    "faiss_changes": {
                                        "faiss_folder": faiss.path,
                                        "model_name": faiss.model,
                                        "weights_name": faiss.weights,
                                    },
                                    "clientId": "direct",
                                    "selectedpage": 1,
                                    "resultsperpage": 1000,
                                    "useGPTasDefault": False,
                                    "returnCLIPConfig": True,
                                    "version": 2,
                                    "activate_caching": False,
                                    "queryMode": "All Images"
                                }
                            }, uri)

                            if not result.get('response', {}).get('success', False):
                                logging.error(f"Error while switching to faiss index: {str(result.get('response', {}).get('message', 'no message'))}")
                                exit(1)
                            logging.info(f"Retry request with new faiss and clip config {faiss.path} ...")
                        else:
                            break

                    ws_results = response.get("results")

                    group_size = int(response.get("group_size", "1"))
                    # add debug info
                    if "debug_info" in ws_results:
                        print(f"debug_info: {ws_results.get('debug_info')}")
                        result_dict.get('debug_info').append(ws_results.get("debug_info"))

                    bestrank = None
                    print(f"calc rank ...")
                    ranks = []
                    for j in range(0, len(ws_results)):
                        if j > max_results:
                            break
                        result = ws_results[j].get("filepath")
                        for answer in topic_dict.get('answers', []):
                            if answer in result:
                                rank = math.ceil((j+1)/group_size)
                                if rank not in ranks:
                                    ranks.append(math.ceil((j+1)/group_size))
                                break

                    if len(ranks) > 0:
                        bestrank = min(ranks)

                    print(f"got rank {bestrank}...")
                    result_dict.get('recall_per_hint').append(bestrank)
                    result_dict.get('ranks_per_hint').append(ranks)

                print(f"append {result_dict}")
                results.append(result_dict)
            except Exception as e:
                print(f"Error: {e}")
                results = None
                break

        print(f"evaluation done.")
        print(f"results: {results}")
        return results