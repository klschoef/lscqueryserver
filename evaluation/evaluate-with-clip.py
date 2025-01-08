import json
import logging
import argparse
import torch
from lsc_shared.clip.core.clip_context import ClipContext
from lsc_shared.clip.core.index_context import IndexContext
from lsc_shared.clip.core.helpers.clip_helper import clip_text_search

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Convert the LSC23 file to JSON.')
parser.add_argument('topic_json_file', help='Topic File in JSON format.')
parser.add_argument('faiss_folder', help='Index file to load the faiss index.')
parser.add_argument('--model_name', default="ViT-H-14", help='Model name like "ViT-H-14"')
parser.add_argument('--pretrained_name', default="laion2b_s32b_b79k", help='Pretrained model name like "laion2b_s32b_b79k"')
args = parser.parse_args()

def main():
    logging.info(f"try to load faiss_folder: {args.faiss_folder}")
    print(f"use model: {args.model_name}, pretrained: {args.pretrained_name} ...")
    index_context = IndexContext(args.faiss_folder)
    clip_context = ClipContext(args.model_name, args.pretrained_name)

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
    max_results = 100

    for topic_dict in lsc_json:
        result_dict = {
            'query_name': topic_dict['query_name'],
            'recall_per_hint': []
        }
        with torch.no_grad():
            for hint in topic_dict.get('hints', []):
                search_results, search_ids, search_distances = clip_text_search(hint, index_context, clip_context, max_results)
                bestrank = None
                for j in range(0,max_results):
                    if bestrank is not None:
                        break

                    result = search_results[j]
                    for answer in topic_dict.get('answers', []):
                        if answer in result:
                            bestrank = j+1

                result_dict.get('recall_per_hint').append(bestrank)

        results.append(result_dict)

    print(f"evaluation done.")
    print(f"results: {results}")
    # save results to json file with model name and pretrained name
    result_file = f"results/results_{args.model_name}_{args.pretrained_name}.json"
    with open(result_file, 'w') as json_file:
        json.dump(results, json_file, indent=4)


if __name__ == '__main__':
    main()