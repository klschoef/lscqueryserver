import json

import websockets

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

    async def get_clip_websocket(self):
        if self.clip_websocket is None:
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
        clip_websocket = await self.get_clip_websocket()
        message.get("content")["query"] = query
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
