import asyncio
import inspect
import uuid

import websockets
from pymongo import MongoClient
import json

from core.query_transform.default_mongodb_query_part_transformers import default_mongodb_query_part_transformers
from core.serializers.object_serializer import ObjectSerializer
from core.serializers.text_query_serializer import TextQuerySerializer


class Client:
    def __init__(self, db_connection, websocket, path, connection_id=str(uuid.uuid4())):
        self.db = db_connection
        self.websocket = websocket
        self.path = path
        self.connection_id = connection_id
        print("Connecting to clip websocket ...")
        self.clip_websocket = None
        self.cached_clip_result = None
        print("Clip websocket connected")

    async def get_clip_websocket(self):
        if self.clip_websocket is None:
            self.clip_websocket = await websockets.connect("ws://cloud6.itec.aau.at:8003")
        return self.clip_websocket

    async def handle(self):
        while True:
            message = await self.websocket.recv()
            await self.handle_message(message)

    async def handle_message(self, message):
        print(f"Received message {message} for client {self.connection_id} on path {self.path}")
        message = json.loads(message)
        message["clientId"] = self.connection_id

        if message.get('source') == "appcomponent":
            content = message.get('content')
            if content:
                version = content.get("version", 1)
                if content.get('type') == "textquery":
                    query = content.get('query')
                    debug_info = {}
                    query_dicts = content.get("query_dicts")
                    if query or query_dicts:
                        print(f"Received query {query}")
                        if not query_dicts:
                            query_dict = TextQuerySerializer.text_query_to_dict(query)
                        else:
                            query_dict = query_dicts[0] # TODO: add temporary support
                        mongo_query = {}

                        selected_page = int(content.get('selectedpage', 1))
                        results_per_page = int(content.get('resultsperpage', 20))
                        skip = (selected_page - 1) * results_per_page
                        if selected_page == 1:
                            self.cached_clip_result = None

                        # build the mongo query
                        for transformer in default_mongodb_query_part_transformers:
                            if transformer.should_use(query_dict):
                                if transformer.__class__.__name__ == "QPTClip" and self.cached_clip_result:
                                    if "$and" not in mongo_query:
                                        mongo_query["$and"] = []
                                    mongo_query["$and"].append(self.cached_clip_result)
                                    break

                                kwargs = {}
                                needed_kwargs = transformer.needed_kwargs()
                                if "clip_websocket" in needed_kwargs:
                                    kwargs["clip_websocket"] = await self.get_clip_websocket()
                                if "message" in needed_kwargs:
                                    kwargs["message"] = message

                                if inspect.iscoroutinefunction(transformer.transform):
                                    await transformer.transform(mongo_query, query_dict, debug_info, **kwargs)
                                else:
                                    transformer.transform(mongo_query, query_dict, debug_info,  **kwargs)

                                if transformer.__class__.__name__ == "QPTClip" and mongo_query.get("$and"):
                                    self.cached_clip_result = mongo_query.get("$and")[-1]

                        # execute the mongo query with pagination
                        total_results = self.db['images'].count_documents(mongo_query)
                        images = self.db['images'].find(mongo_query, {"filepath": 1, "datetime": 1, "heart_rate": 1}).skip(skip).limit(results_per_page)

                        if version >= 2:
                            results = ObjectSerializer.objects_to_serialized_json(list(images))
                        else:
                            results = [image.get('filepath') for image in images]

                        # build result object
                        result = {"num": len(results), "totalresults": total_results, "results": results, "debug_info": debug_info}
                        print(f"send result {result}")
                        await self.websocket.send(json.dumps(result))
                    else:
                        print("No query found in content")
                elif content.get('type') == "metadataquery":
                    result = {"type": "metadata", "num": 1, "totalresults": 1, "results": []}
                    images = self.db['images'].find({"filepath": content.get('imagepath')})
                    # make all fields serializable
                    result['results'] = ObjectSerializer.objects_to_serialized_json(images)

                    print(f"send result {result}")
                    await self.websocket.send(json.dumps(result))
                elif content.get('type') == "objects":
                    objects = self.db["objects"].find({}, {"name": 1}).sort({"name": 1})
                    objects = ObjectSerializer.objects_to_serialized_json(objects)
                    await self.websocket.send(json.dumps({"type": "objects", "num": len(objects), "results": objects}))
                elif content.get('type') == "concepts":
                    concepts = self.db["concepts"].find({}, {"name": 1}).sort({"name": 1})
                    concepts = ObjectSerializer.objects_to_serialized_json(concepts)
                    await self.websocket.send(json.dumps({"type": "concepts", "num": len(concepts), "results": concepts}))
                elif content.get('type') == "places":
                    places = self.db["places"].find({}, {"name": 1}).sort({"name": 1})
                    places = ObjectSerializer.objects_to_serialized_json(places)
                    await self.websocket.send(json.dumps({"type": "places", "num": len(places), "results": places}))
                elif content.get('type') == "texts":
                    texts = self.db["texts"].find({}, {"name": 1}).sort({"name": 1})
                    texts = ObjectSerializer.objects_to_serialized_json(texts)
                    await self.websocket.send(json.dumps({"type": "texts", "num": len(texts), "results": texts}))
                else:
                    print(f"Unknown content type {content.get('type')}")
                    await self.websocket.send(json.dumps({"type": "error", "error": "unknown content type"}))
        else:
            print(f"Unknown source type {message.get('source')}")


class Server:
    def __init__(self):
        print("try to connect to mongodb...")
        self.client = MongoClient('mongodb://extreme00.itec.aau.at:27017')
        self.db = self.client['lsc']

    async def handler(self, websocket, path):
        print(f"New connection {path}, {websocket.remote_address}")
        client = Client(self.db, websocket, path)
        await client.handle()

    def start(self):
        print("Starting server ...")
        start_server = websockets.serve(self.handler, '', 8080)

        asyncio.get_event_loop().run_until_complete(start_server)
        print("Server started")
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    server = Server()
    server.start()
