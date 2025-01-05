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
        if image_document.get('metadata', {}).get('open_clip_metadata', {}).get('added_line_row') is not None:
            print(f"OpenClip metadata already exists for {image_document.get('_id')}. Skipping.")
            #return image, image_document

        print(f"Processing {image_document.get('filepath')} with OpenClip...")

        clip_response = asyncio.run(self.get_clip_response_sync({
            'content': {
                'type': 'indexrequest',
                'filepath': image_document.get('filepath')
            }
        }))
        clip_entry_metadata = clip_response.get('clip_entry_metadata') if isinstance(clip_response, dict) else None
        if clip_entry_metadata and clip_entry_metadata.get('added_line_row') is not None:
            print(f"OpenClip added index. (metadata: {clip_response.get('clip_entry_metadata')})")
            mongo_collection.update_one({'_id': image_document.get('_id')}, {'$set': {
                'metadata.open_clip_metadata': clip_response.get('clip_entry_metadata'),
                'l2dist': clip_entry_metadata.get('l2_to_last_one')
            }})
            # Re-fetch the updated document from MongoDB
            image_document = mongo_collection.find_one({'_id': image_document.get('_id')})
        else:
            print(f"OpenClip did not add index. (response: {clip_response})")
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
        self.clip_websocket = await websockets.connect(os.getenv('CLIP_URL'))
        return self.clip_websocket
