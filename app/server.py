import asyncio
import uuid

import websockets
from pymongo import MongoClient
import json

from core.serializers.object_serializer import ObjectSerializer


class Client:
    def __init__(self, db_connection, websocket, path, connection_id=str(uuid.uuid4())):
        self.db = db_connection
        self.websocket = websocket
        self.path = path
        self.connection_id = connection_id
        print("Connecting to clip websocket ...")
        self.clip_websocket = None
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
                if content.get('type') == "textquery":
                    query = content.get('query')
                    if query:
                        print(f"Received query {query}")
                        clip_websocket = await self.get_clip_websocket()
                        # First check if there is any CLIP Search
                        await clip_websocket.send(json.dumps(message))
                        clip_response = await clip_websocket.recv()
                        clip_response = json.loads(clip_response)
                        # If CLIP Search is needed, do the clip search, and fetch the image paths
                        # Do also pagination

                        selected_page = int(content.get('selectedpage', 1))
                        results_per_page = int(content.get('resultsperpage', 20))
                        skip = (selected_page - 1) * results_per_page
                        images = self.db['images'].find({}, {"filepath": 1}).skip(skip).limit(results_per_page)
                        # self.db['images'].find({'year': 2020})[:10]
                        result = {"num": 0, "totalresults": 0, "results": [image.get('filepath') for image in images]}
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
                else:  # TODO: add logic for objects, concepts, places and texts like in server.js lines from 264
                    print(f"Unknown content type {content.get('type')}")
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
