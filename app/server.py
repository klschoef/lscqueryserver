import asyncio
import uuid

import websockets
from pymongo import MongoClient
import json

from core.serializers.object_serializer import ObjectSerializer


class Client:
    def __init__(self, db_connection, websocket, path, connection_id=uuid.uuid4()):
        self.db = db_connection
        self.websocket = websocket
        self.path = path
        self.connection_id = connection_id

    async def handle(self):
        while True:
            message = await self.websocket.recv()
            await self.handle_message(message)

    async def handle_message(self, message):
        print(f"Received message {message} for client {self.connection_id} on path {self.path}")
        message = json.loads(message)
        # {"source":"appcomponent","content":{"type":"textquery","clientId":"direct","query":"-o person","maxresults":2000,"resultsperpage":56,"selectedpage":"1","queryMode":"all"}}
        if message.get('source') == "appcomponent":
            content = message.get('content')
            if content:
                if content.get('type') == "textquery":
                    query = content.get('query')
                    if query:
                        print(f"Received query {query}")
                        selected_page = int(content.get('selectedpage', 1))
                        results_per_page = int(content.get('resultsperpage', 20))
                        skip = (selected_page - 1) * results_per_page
                        images = self.db['images'].find({}, {"filepath": 1}).skip(skip).limit(results_per_page)
                        #self.db['images'].find({'year': 2020})[:10]
                        result = {"num": 0, "totalresults": 0, "results": [image.get('filepath') for image in images]}
                        print(f"send result {result}")
                        await self.websocket.send(json.dumps(result))
                    else:
                        print("No query found in content")
                elif content.get('type') == "metadataquery":
                    result = {"type": "metadata", "num": 1, "totalresults": 1, "results": []}
                    images = self.db['images'].find({"filepath": content.get('imagepath')})
                    # replace the id, which is a idObject to string, to make it serializable
                    result['results'] = ObjectSerializer.objects_to_serialized_json(images)

                    print(f"send result {result}")
                    await self.websocket.send(json.dumps(result))
                else:
                    print(f"Unknown content type {content.get('type')}")
        else:
            print(f"Unknown source type {message.get('source')}")

class Server:
    def __init__(self):
        print("try to connect to mongodb...")
        self.client = MongoClient('mongodb://extreme00.itec.aau.at:27017')
        print("connected to mongodb")
        self.db = self.client['lsc']

    async def handler(self, websocket, path):
        print(f"New connection {path}, {websocket.remote_address}")
        client = Client(self.db, websocket, path)
        await client.handle()

    def start(self):
        print("Starting server")
        start_server = websockets.serve(self.handler, '', 8080)

        print("Server started")
        asyncio.get_event_loop().run_until_complete(start_server)
        print("Server run until complete")
        asyncio.get_event_loop().run_forever()
        print("Server run forever")

if __name__ == "__main__":
    server = Server()
    server.start()