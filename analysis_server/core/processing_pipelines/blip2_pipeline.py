import datetime
from core.processing_pipelines.base_pipeline import BasePipeline
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from dotenv import load_dotenv
load_dotenv()
import torch
import datetime

class Blip2Pipeline(BasePipeline):

    def __init__(self):
        # Load the BLIP processor and model
        print(f"Loading BLIP-2 processor...")
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
        print(f"Loading BLIP-2 model to {self.device}...")
        self.model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl").to(self.device)

    def process(self, image, image_document, mongo_collection, *args, **kwargs) -> tuple:
        if image_document.get('metadata', {}).get('blip2_metadata', {}).get('description') is not None:
            print(f"BLIP-2 metadata already exists for {image_document.get('_id')}. Skipping.")
            return image, image_document

        start_blip_time = datetime.datetime.now()
        # Prepare inputs for the model
        prompt = "A detailed description of the scene, objects, and background."
        inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)
        #inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        # Generate a description
        generated_ids = self.model.generate(**inputs, max_new_tokens=150, do_sample=True)
        description = self.processor.decode(generated_ids[0], skip_special_tokens=True)

        end_blip_time = datetime.datetime.now()
        start_mongo_update_time = datetime.datetime.now()

        mongo_collection.update_one({'_id': image_document.get('_id')}, {'$set': {
            'blip2caption': description,
            'metadata.blip2_metadata': {
                'description': description,
                'generated_at': datetime.datetime.now(),
                'blip2_model': self.model.name_or_path
            }
        }})
        # Re-fetch the updated document from MongoDB
        image_document = mongo_collection.find_one({'_id': image_document.get('_id')})

        end_mongo_update_time = datetime.datetime.now()

        blip_duration = end_blip_time - start_blip_time
        mongo_update_duration = end_mongo_update_time - start_mongo_update_time

        # Ausgabe der Zeiten
        print(f"BLIP processing time: {blip_duration.total_seconds()} seconds")
        print(f"MongoDB update time: {mongo_update_duration.total_seconds()} seconds")

        return image, image_document
