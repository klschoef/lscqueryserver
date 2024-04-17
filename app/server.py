import asyncio
import websockets
from pymongo import MongoClient

from core import settings
from core.models.client import Client


class Server:
    def __init__(self):
        print("try to connect to mongodb...")
        self.mongo_client = MongoClient(settings.MONGO_DB_URL)
        self.db = self.mongo_client[settings.MONGO_DB_DATABASE]

    async def handler(self, websocket, path):
        print(f"New connection {path}, {websocket.remote_address}")
        # Main Logic is handled in the Client class
        client = Client(self.db, websocket, path)
        await client.handle()

    def start(self):
        print("Starting server ...")
        start_server = websockets.serve(self.handler, '', settings.SERVER_PORT)

        asyncio.get_event_loop().run_until_complete(start_server)
        print(f"Server started at Port {settings.SERVER_PORT}")
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    server = Server()
    server.start()
