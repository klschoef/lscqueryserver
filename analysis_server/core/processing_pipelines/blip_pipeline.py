import asyncio
import datetime
import json
import websockets
from core.processing_pipelines.base_pipeline import BasePipeline
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
import os

class BlipPipeline(BasePipeline):

    def __init__(self):
        # Load the BLIP processor and model
        print(f"Loading BLIP processor...")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        print(f"Loading BLIP model...")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def process(self, image, image_document, mongo_collection, *args, **kwargs) -> tuple:
        if image_document.get('metadata', {}).get('blip_metadata', {}).get('description') is not None:
            print(f"BLIP metadata already exists for {image_document.get('_id')}. Skipping.")
            return image, image_document
        inputs = self.processor(images=image, return_tensors="pt")
        out = self.model.generate(**inputs)
        description = self.processor.decode(out[0])

        mongo_collection.update_one({'_id': image_document.get('_id')}, {'$set': {
            'blipcaption': description,
            'metadata.blip_metadata': {
                'description': description,
                'generated_at': datetime.datetime.now(),
                'blip_model': self.model.name_or_path
            }
        }})
        # Re-fetch the updated document from MongoDB
        image_document = mongo_collection.find_one({'_id': image_document.get('_id')})
        return image, image_document
