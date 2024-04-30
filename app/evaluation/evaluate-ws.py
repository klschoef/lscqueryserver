import json
import argparse
import asyncio
import websockets

clipdata = []
parser = argparse.ArgumentParser(description='Convert the LSC23 file to JSON.')
parser.add_argument('topic_json_file', help='Topic File in JSON format.')
parser.add_argument('--versions', default="0", help='How much GPT versions should be used')
parser.add_argument('--model_name', default="ViT-H-14", help='Model name like "ViT-H-14"')
parser.add_argument('--pretrained_name', default="laion2b_s32b_b79k", help='Pretrained model name like "laion2b_s32b_b79k"')

args = parser.parse_args()

print(f"use model: {args.model_name}, pretrained: {args.pretrained_name} ...")

print(f"load json file: {args.topic_json_file} ...")
lsc_json_file = args.topic_json_file
lsc_json = None
# load the json file
with open(lsc_json_file) as f:
    lsc_json = json.load(f)

if lsc_json is None:
    print(f"Error: could not load {lsc_json_file}")
    exit(1)

print(f"start evaluation ...")

results = []
MAXRESULTS = 100

loop = asyncio.get_event_loop()

async def send_and_receive_message():
    uri = "ws://localhost:8080"
    print(f"try to connect to server {uri} ...")
    async with websockets.connect(uri) as websocket:
        print(f"connected to server {uri} ...")
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
                            "resultsperpage": 200,
                            "version": 2,
                            "query_dicts": [
                                {
                                    "clip": {
                                        "query": hint,
                                        "subqueries": {
                                            "variants": args.versions
                                        }
                                    }
                                }
                            ],
                            "queryMode": {"id": "all", "name": "All Images"}
                        }
                    })

                    #print(f"send request: {request}")
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

                    print(f"got rank {bestrank}...")
                    result_dict.get('recall_per_hint').append(bestrank)

                print(f"append {result_dict}")
                results.append(result_dict)
            except Exception as e:
                print(f"Error: {e}")

        print(f"evaluation done.")
        print(f"results: {results}")
        # save results to json file with model name and pretrained name
        result_file = f"evaluation/results/results_{args.model_name}_{args.pretrained_name}_versions_{args.versions}.json"
        with open(result_file, 'w') as json_file:
            json.dump(results, json_file, indent=4)

asyncio.get_event_loop().run_until_complete(send_and_receive_message())