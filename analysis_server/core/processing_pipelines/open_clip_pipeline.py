import asyncio
import json
import websockets
from core.processing_pipelines.base_pipeline import BasePipeline
from dotenv import load_dotenv
load_dotenv()
import os

class OpenClipPipeline(BasePipeline):

    def __init__(self):
        self.clip_websocket = None

    def process(self, image, image_document, mongo_collection, *args, **kwargs) -> tuple:
        """Synchronously process an image and handle WebSocket communication."""
        # Run the async method synchronously using asyncio.run
        clip_response = asyncio.run(self.get_clip_response_sync({
            'content': {
                'type': 'indexrequest',
                'filepath': image_document.get('filepath')
            }
        }))
        print(clip_response)
        return image, image_document

    async def get_clip_response_sync(self, message_dict):
        """Async helper method that wraps get_clip_response for sync use."""
        return await self.get_clip_response(message_dict)

    async def get_clip_response(self, message_dict):
        """Sends message to WebSocket and retrieves the response asynchronously."""
        clip_websocket = await self.get_clip_websocket()  # Ensure this is awaited
        await clip_websocket.send(json.dumps(message_dict))
        clip_response = await clip_websocket.recv()
        return json.loads(clip_response)

    async def get_clip_websocket(self):
        if self.clip_websocket is None:
            self.clip_websocket = await websockets.connect(os.getenv('CLIP_URL'))
        return self.clip_websocket
