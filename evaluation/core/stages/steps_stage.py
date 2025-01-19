import asyncio
import json
import os
import time

from core.stages.base_stage import BaseStage
import logging

from core.utils.file_util import get_project_related_file_path
from core.utils.websocket_util import send_and_receive_message


class StepsStage(BaseStage):

    def run(self, config):
        project_folder = config.project_folder
        for step in config.steps:
            logging.info(f"start step: {step.name}")
            lsc_server_url = config.lsc_server_url
            if step.type == "faiss":
                logging.info(f"faiss step: {step.name}")
                faiss = step.faiss
                if faiss is None:
                    logging.error(f"Error: no faiss config found for step {step.name}")
                    exit(1)
                for topic_file in config.topic_files:
                    result_file = get_project_related_file_path(project_folder, f"results/single_results/{step.name}/{topic_file.split('/')[-1]}/results_{step.name}.json")

                    if os.path.exists(result_file):
                        logging.info(f"skip {result_file} because it already exists.")
                        continue

                    logging.info(f"load topic file {topic_file} ...")
                    lsc_json = None
                    with open(get_project_related_file_path(project_folder, topic_file), "r") as f:
                        lsc_json = json.load(f)

                    if lsc_json is None:
                        logging.error(f"Error: could not load topic file {topic_file}")
                        exit(1)

                    results = None
                    while results is None:
                        results = asyncio.run(send_and_receive_message(lsc_json, lsc_server_url, faiss))
                        if results is None:
                            logging.error(f"Error: could not get results for topic file {topic_file}. Retry after 2 seconds.")
                            time.sleep(2)

                    folder_path = "/".join(result_file.split("/")[:-1])
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    with open(result_file, 'w') as json_file:
                        json.dump(results, json_file, indent=4)

