import asyncio
import json
import os
import time

from core.stages.base_stage import BaseStage
import logging

from core.utils.file_util import get_project_related_file_path
from core.utils.websocket_util import LSCWebsocketClient, LSCServerNoResultsException


class StepsStage(BaseStage):

    def run(self, config):
        project_folder = config.project_folder
        for step in config.steps:
            logging.info(f"start step: {step.name}")
            lsc_server_url = config.lsc_server_url
            lsc_websocket = LSCWebsocketClient(lsc_server_url)

            faiss = None
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

                results = []
                max_results = 100
                max_retries = 10
                retries = 0
                retries_pow_base = 2
                loop = asyncio.get_event_loop()

                for topic_dict in lsc_json:
                    logging.info(f"start evaluation for {topic_dict['query_name']} for {result_file} ...")

                    result_dict = {
                        'query_name': topic_dict['query_name'],
                        'recall_per_hint': [],
                        'ranks_per_hint': [],
                        'debug_info': []
                    }
                    for hint in topic_dict.get('hints', []):
                        exception_appeared = False
                        while True:
                            try:
                                request = lsc_websocket.create_request(hint, useGPTasDefault=(step.type == "solr"), solrCore=step.solr.core if step.solr else None)
                                if exception_appeared:
                                    loop.run_until_complete(lsc_websocket.create_connection())
                                    exception_appeared = False
                                response = loop.run_until_complete(lsc_websocket.send_and_receive_faiss_query(request, faiss))
                                lsc_websocket.append_to_result_dict(response, topic_dict.get('answers', []), result_dict, max_results, stop_if_no_results=step.stop_if_no_results)
                                retries = 0
                                break
                            except LSCServerNoResultsException as e:
                                logging.exception(f"No results for {hint}")
                                exception_appeared = True
                                exit(1)
                                retries = 0
                                break
                            except Exception as e:
                                exception_appeared = True
                                if retries >= max_retries:
                                    logging.critical(f"Max retries reached for {hint}")
                                    exit(1)
                                retries += 1
                                seconds_to_wait = retries_pow_base**retries
                                logging.exception(f"Retry (wait {seconds_to_wait} seconds) after error {str(e)} for {hint}")
                                time.sleep(seconds_to_wait)

                    results.append(result_dict)

                folder_path = "/".join(result_file.split("/")[:-1])
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                with open(result_file, 'w') as json_file:
                    json.dump(results, json_file, indent=4)


