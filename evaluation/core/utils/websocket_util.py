import json
import logging
import math
import websockets


class LSCServerException(Exception):
    pass


class LSCServerSwitchFaissException(Exception):
    pass

class LSCServerNoResultsException(Exception):
    pass

class LSCWebsocketClient:
    def __init__(self, url):
        self.websocket = None
        self.url = url

    async def create_connection(self):
        logging.info(f"create new websocket connection to {self.url} ...")
        self.websocket = await websockets.connect(self.url)
        logging.info(f"websocket connection created to {self.url}")

    def get_faiss_information_out_of_results(self, response):
        clip_config = response.get("debug_info", {}).get("clip_config", {})
        faiss_folder = clip_config.get("faiss_folder")
        model_name = clip_config.get("model_name")
        weights_name = clip_config.get("weights_name")
        return faiss_folder, model_name, weights_name

    def compare_clip_faiss_config(self, response, faiss):
        faiss_folder, model_name, weights_name = self.get_faiss_information_out_of_results(response)
        if faiss_folder != faiss.path or model_name != faiss.model or weights_name != faiss.weights:
            return False
        return True

    async def switch_faiss_index(self, faiss):
        logging.info(
            f"switch to faiss index {faiss.path} (This can take minutes to hours depending on CLIP server's internet connection, and cache state) ...")

        result = await self.send_and_receive({
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
        })

        if not result.get('response', {}).get('success', False):
            error_message = f"Error while switching to faiss index: {str(result.get('response', {}).get('message', 'no message'))}"
            logging.error(error_message)
            raise LSCServerSwitchFaissException(
                f"Error while switching to faiss index: {str(result.get('response', {}).get('message', 'no message'))}")

        return True

    async def send_and_receive(self, json_request):
        if self.websocket is None or self.websocket.closed:
            await self.create_connection()

        logging.debug(f"Send request to {self.url}: {json_request}")
        await self.websocket.send(json.dumps(json_request))
        while True:
            response = json.loads(await self.websocket.recv())
            logging.debug(f"Received from {self.url}: {response}")
            if response.get("type", "") == "progress":
                logging.info(f"Progress from {self.url}: {response.get('message', '')}")
            elif response.get("type", "") == "error":
                logging.error(f"LSC Server Error: {response.get('error', '')}")
                raise LSCServerException(response.get('error', ''))
            else:
                return response

    async def send_and_receive_faiss_query(self, json_request, faiss):
        response = await self.send_and_receive(json_request)
        hint = json_request.get("content", {}).get("query", "")

        if faiss and not hint.startswith("-") and not self.compare_clip_faiss_config(response, faiss):
            await self.switch_faiss_index(faiss)
            logging.info(f"Retry request with new faiss and clip config {faiss.path} ...")
            response = await self.send_and_receive_faiss_query(json_request, faiss)

        return response

    def create_request(self, hint, resultsperpage=1000, useGPTasDefault=False, solrCore="gpt"):
        return {
            "source": "appcomponent",
            "content": {
                "type": "textquery",
                "clientId": "direct",
                "selectedpage": 1,
                "resultsperpage": resultsperpage,
                "useGPTasDefault": useGPTasDefault,
                "solrCore": solrCore,
                "returnCLIPConfig": True,
                "version": 2,
                "query": hint,
                "activate_caching": False,
                "queryMode": "All Images"
            }
        }

    def append_to_result_dict(self, response, answers, result_dict, max_results=100, stop_if_no_results=True):
        ws_results = response.get("results")
        if stop_if_no_results and (ws_results is None or len(ws_results) == 0):
            raise LSCServerNoResultsException("No results found for hint")

        group_size = int(response.get("group_size", "1"))
        # add debug info
        if "debug_info" in response:
            logging.debug(f"debug_info: {response.get('debug_info')}")
            result_dict.get('debug_info').append(response.get("debug_info"))

        bestrank = None
        logging.info(f"calc rank ...")
        ranks = []
        for j in range(0, len(ws_results)):
            if j > max_results:
                break
            result = ws_results[j].get("filepath")
            for answer in answers:
                if answer in result:
                    rank = math.ceil((j + 1) / group_size)
                    if rank not in ranks:
                        ranks.append(math.ceil((j + 1) / group_size))
                    break

        if len(ranks) > 0:
            bestrank = min(ranks)

        logging.info(f"got rank {bestrank}...")
        result_dict.get('recall_per_hint').append(bestrank)
        result_dict.get('ranks_per_hint').append(ranks)


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
