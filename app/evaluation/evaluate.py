import json
import argparse
import asyncio
from pymongo import MongoClient

from core import settings
from core.message_handlers.handlers.message_query import MessageQuery
from core.models.client import Client
from core.models.client_request import ClientRequest

clipdata = []
parser = argparse.ArgumentParser(description='Convert the LSC23 file to JSON.')
parser.add_argument('topic_json_file', help='Topic File in JSON format.')
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
client = Client(MongoClient(settings.MONGO_DB_URL), None, None)
message_query_handler = MessageQuery()

for topic_dict in lsc_json:
    result_dict = {
        'query_name': topic_dict['query_name'],
        'recall_per_hint': []
    }
    for hint in topic_dict.get('hints', []):
        # TODO: do the search for hint
        #input = clip_package.tokenize(hint, context_length=int(args.tokenizer_context_length)).to(device)
        #text_features = model.encode_text(input).cpu()
        #D, I = index.search(text_features, MAXRESULTS)

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
                                "variants": "1"
                            }
                        }
                    }
                ],
                "queryMode": {"id": "all", "name": "All Images"}
            }
        })

        request = ClientRequest(json.dumps(request))

        result = loop.run_until_complete(message_query_handler.handle(request, client))

        bestrank = None
        for j in range(0,MAXRESULTS):
            if bestrank is not None:
                break

            #idx = I[0][j] #+ 1
            result = "any result TODO here"
            for answer in topic_dict.get('answers', []):
                if answer in result:
                    bestrank = j+1

        result_dict.get('recall_per_hint').append(bestrank)

    results.append(result_dict)

print(f"evaluation done.")
print(f"results: {results}")
# save results to json file with model name and pretrained name
result_file = f"evaluation/results/results_{args.model_name}_{args.pretrained_name}.json"
with open(result_file, 'w') as json_file:
    json.dump(results, json_file, indent=4)
