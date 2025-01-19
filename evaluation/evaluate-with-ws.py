import json
import logging
import argparse
import math
import asyncio
import websockets

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='')
parser.add_argument('topic_json_file', help='Topic File in JSON format.')
parser.add_argument('ws_url', help='URL to LSC Websocket')
parser.add_argument('result_file_name', help='Name of the result file')
args = parser.parse_args()
loop = asyncio.get_event_loop()

async def send_and_receive_message(lsc_json):
    uri = "ws://localhost:8080"
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
                'debug_info': []
            }
            try:
                for hint in topic_dict.get('hints', []):
                    request = ({
                        "source": "appcomponent",
                        "content": {
                            "type": "textquery",
                            "clientId": "direct",
                            "selectedpage": 1,
                            "resultsperpage": 1000,
                            "useGPTasDefault": False,
                            "version": 2,
                            "query": hint,
                            "queryMode": "All Images"
                        }
                    })

                    print(f"send request for: {hint}")

                    await websocket.send(json.dumps(request))
                    response = {}
                    error = False
                    while True:
                        response = await websocket.recv()
                        # print(f"received response: {response}")
                        response = json.loads(response)
                        if "results" in response:
                            break
                        elif response.get("type", "") == "progress":
                            print(f"Progress: {response.get('message', '')}")
                        if response.get("type", "") == "error":
                            print(f"Error: {response.get('error', '')}")
                            error = True
                            break

                    if error:
                        continue

                    ws_results = response.get("results")
                    group_size = int(response.get("group_size", "1"))
                    # add debug info
                    if "debug_info" in ws_results:
                        print(f"debug_info: {ws_results.get('debug_info')}")
                        result_dict.get('debug_info').append(ws_results.get("debug_info"))

                    bestrank = None
                    print(f"calc rank ...")
                    for j in range(0, len(ws_results)):
                        if bestrank is not None:
                            break

                        #idx = I[0][j] #+ 1
                        result = ws_results[j].get("filepath")
                        for answer in topic_dict.get('answers', []):
                            if answer in result:
                                bestrank = j+1

                    if bestrank:
                        bestrank = math.ceil(bestrank/group_size)

                    print(f"got rank {bestrank}...")
                    result_dict.get('recall_per_hint').append(bestrank)

                print(f"append {result_dict}")
                results.append(result_dict)
            except Exception as e:
                print(f"Error: {e}")

        print(f"evaluation done.")
        print(f"results: {results}")
        # save results to json file with model name and pretrained name
        result_file = f"results/{args.result_file_name}"
        with open(result_file, 'w') as json_file:
            json.dump(results, json_file, indent=4)

def main():

    print(f"load json file: {args.topic_json_file} ...")
    lsc_json_file = args.topic_json_file
    lsc_json = None
    # load the json file
    with open(lsc_json_file) as f:
        lsc_json = json.load(f)

    if lsc_json is None:
        print(f"Error: could not load {lsc_json_file}")
        exit(1)

    asyncio.get_event_loop().run_until_complete(send_and_receive_message(lsc_json))


if __name__ == '__main__':
    main()