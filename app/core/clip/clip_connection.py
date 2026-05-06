import json

import websockets
from websockets.exceptions import ConnectionClosed

from core import settings


class ClipResponse:

    def __init__(self, results, remote_response=None):
        self.results = results
        self.remote_response = remote_response


class ClipConnection:

    """
    TODO: Add additional class, which loads a clip csv, and do it with the local clip client. (Also use a local client for it)
    """
    def __init__(self, client, use_local_clip=False, clip_model=None, clip_pretrained=None):
        self.client = client
        self.clip_websocket = None
        self.use_local_clip = use_local_clip
        self.clip_model = clip_model
        self.clip_pretrained = clip_pretrained
        self.loaded_clip_config = None

    async def get_clip_websocket(self):
        if self.clip_websocket is None or getattr(self.clip_websocket, "closed", False):
            self.clip_websocket = await websockets.connect(settings.CLIP_URL)
        return self.clip_websocket

    async def query(self, query, message, results_per_page=None, max_results=None, event_type=None, pathprefix=None):
        if self.use_local_clip:
            return self.query_local(query, message, results_per_page, max_results, event_type, pathprefix)
        else:
            return await self.query_remote(query, message, results_per_page, max_results, event_type, pathprefix)

    def query_local(self, query, message, results_per_page=None, max_results=None, event_type=None, pathprefix=None):
        # TODO: add logic for local clip (the whole message is not needed in that case,
        # just the query and the pagination from message)
        pass

    async def query_raw(self, content):
        message = {
            "content": content
        }

        try:
            clip_websocket = await self.get_clip_websocket()
            await clip_websocket.send(json.dumps(message))
            clip_response = await clip_websocket.recv()
        except ConnectionClosed:
            # clip server closes some request-response sockets (e.g. faiss_info/faiss_change),
            # so reconnect and retry once.
            self.clip_websocket = None
            clip_websocket = await self.get_clip_websocket()
            await clip_websocket.send(json.dumps(message))
            clip_response = await clip_websocket.recv()

        clip_response = json.loads(clip_response)
        return clip_response

    def _get_target_clip_config(self, query_model):
        if query_model == "siglip2":
            return {
                "faiss_folder": settings.SIGLIP2_FAISS_FOLDER,
                "model_name": settings.SIGLIP2_MODEL_NAME,
                "weights_name": settings.SIGLIP2_WEIGHTS_NAME,
            }
        return {
            "faiss_folder": settings.CLIP_FAISS_FOLDER,
            "model_name": settings.CLIP_MODEL_NAME,
            "weights_name": settings.CLIP_WEIGHTS_NAME,
        }

    async def ensure_query_model_loaded(self, query_model, strict=False):
        if self.use_local_clip:
            return

        target_config = self._get_target_clip_config(query_model)
        has_target_config = all(target_config.values())

        if strict and not has_target_config:
            raise ValueError(
                f"Missing {query_model} configuration. "
                f"Please set environment values for faiss/model/weights."
            )

        if not has_target_config:
            return

        if self.loaded_clip_config is None:
            info_response = await self.query_raw({"type": "faiss_info"})
            self.loaded_clip_config = (info_response or {}).get("info")

        current_config = self.loaded_clip_config or {}
        if current_config.get("faiss_path") == target_config.get("faiss_folder") \
                and current_config.get("model_name") == target_config.get("model_name") \
                and current_config.get("weights_name") == target_config.get("weights_name"):
            return

        change_response = await self.query_raw({
            "type": "faiss_change",
            "faiss_changes": target_config
        })

        if not change_response.get("success", False):
            raise ValueError(f"Failed to change faiss/model: {change_response.get('message')}")

        self.loaded_clip_config = {
            "faiss_path": target_config.get("faiss_folder"),
            "model_name": target_config.get("model_name"),
            "weights_name": target_config.get("weights_name"),
        }

    async def query_remote(self, query, message, results_per_page=None, max_results=None, event_type=None, pathprefix=None):
        # store the old values
        old_results_per_page = message.get("content").get("resultsperpage")
        old_max_results = message.get("content").get("maxresults")

        # change max page values
        if results_per_page:
            message.get("content")["resultsperpage"] = results_per_page
        if max_results:
            message.get("content")["maxresults"] = max_results

        # change event_type if required
        if event_type:
            message.get("content")["type"] = event_type

        if pathprefix is not None:
            message.get("content")["pathprefix"] = pathprefix

        # do the clip request
        message.get("content")["query"] = query
        try:
            clip_websocket = await self.get_clip_websocket()
            await clip_websocket.send(json.dumps(message))
            clip_response = await clip_websocket.recv()
        except ConnectionClosed:
            self.clip_websocket = None
            clip_websocket = await self.get_clip_websocket()
            await clip_websocket.send(json.dumps(message))
            clip_response = await clip_websocket.recv()

        clip_response = json.loads(clip_response)
        results = []
        if clip_response and clip_response.get("results") and len(clip_response.get("results")) > 0:
            results = clip_response.get("results")

        # restore the original sizes
        message.get("content")["resultsperpage"] = old_results_per_page
        message.get("content")["maxresults"] = old_max_results

        return ClipResponse(results, clip_response)
