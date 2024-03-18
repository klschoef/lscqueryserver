import json

from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase

class QPTClip(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("clip"))

    def needed_kwargs(self):
        return ["clip_websocket", "message"]

    async def transform(self, result_object, query_dict, *args, **kwargs):
        clip_websocket = kwargs.get("clip_websocket")
        message = kwargs.get("message")
        await clip_websocket.send(json.dumps(message))
        clip_response = await clip_websocket.recv()
        clip_response = json.loads(clip_response)
        if clip_response and clip_response.get("results") and len(clip_response.get("results")) > 0:
            result_object["filepath"] = {"$in": clip_response.get("results")}