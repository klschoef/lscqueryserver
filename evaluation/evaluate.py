import json
import logging
import argparse
import os
import time

import math
import asyncio
import websockets
from core.models.config import Config
from core.stages.steps_stage import StepsStage
from core.utils.file_util import get_project_related_file_path

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='')
parser.add_argument('project_folder', help='Path to project folder')
parser.add_argument('--config_file_name', default='config.json', help='Name of the config file')
args = parser.parse_args()
loop = asyncio.get_event_loop()

def main():
    config_file_path = f"{args.project_folder}/{args.config_file_name}"
    print(f"load config file: {config_file_path} ...")
    config_json = None
    # load the json file
    with open(config_file_path) as f:
        config_json = json.load(f)

    if config_json is None:
        print(f"Error: could not load config file {config_file_path}")
        exit(1)

    config = Config.from_json(config_json, project_folder=args.project_folder)

    stages = [
        StepsStage(),
    ]

    for stage in stages:
        stage.run(config)

    summary = [["type", "name", "model", "weight", "topic", "r@k summary"]]
    k_values = [1, 3, 5, 10, 20, 50, 100]
    include_hints = [0, 1, 2, 3, 4, 5]
    for step in config.steps:
        folder_name = f"results/single_results/{step.name}"
        for topic_name in [t.split("/")[-1] for t in config.topic_files]:
            single_results_path = get_project_related_file_path(config.project_folder, f"{folder_name}/{topic_name}")
            # find the json file in the folder
            json_file = None  # Initialize json_file variable
            for file in os.listdir(single_results_path):
                if file.endswith(".json"):
                    json_file = os.path.join(single_results_path, file)
                    break  # Stop the search once the first json file is found

            if json_file:
                # Code to process the JSON file
                print(f"Processing {json_file}")
                summary_entry = ["clip", step.name, step.faiss.model, step.faiss.weights, topic_name]

                with open(json_file, 'r') as file:
                    data = json.load(file)
                    csv_output = []
                    for hint_index in include_hints:
                        csv_row = []
                        #csv_row.append(f"Hint-{hint_index+1}")
                        for k in k_values:
                            csv_row.append(get_mean_recall_at_k_for_all_results(data, hint_index, k))
                        csv_output.append(csv_row)

                    csv_summary = 0
                    hints_amount = len(csv_output)
                    for hint in range(hints_amount,0,-1):
                        for i in range(1, len(k_values)+1):
                            csv_summary += csv_output[hints_amount-hint][i-1]*hint/i

                    summary_entry.append(csv_summary)
                summary.append(summary_entry)
            else:
                print(f"No JSON file found in {single_results_path}")

    logging.info(f"calc summaries: {summary}")
    print("\n".join([",".join([str(x) for x in row]) for row in summary]))


def get_mean_recall_at_k_for_all_results(dict_array, hint_index, k):
    total = 0
    for query in dict_array:
        total += get_recall_at_k_for_quest_results(query, hint_index, k)

    return total / len(dict_array)


"""
get the recall at k value for one single query with a given hint index. Returns 1 (found) or 0 (not found in the recall@k)
    {
        "query_name": "LSC23-KIS07",
        "recall_per_hint": [
            63,
            null,
            40,
            5,
            1,
            2
        ]
    },
    
"""


def get_recall_at_k_for_quest_results(query, hint_index, k):
    found_index = query.get('recall_per_hint')[hint_index]

    if found_index is None:
        return 0

    return 1 if found_index <= k else 0


if __name__ == '__main__':
    main()