import argparse
from dotenv import load_dotenv
import os
from PIL import Image

from core.helpers.mongo_helper import get_mongo_collection
from core.processing_pipelines.blip2_pipeline import Blip2Pipeline
from pathlib import Path
import os

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process an image to extract metadata and resize.")
    parser.add_argument('--image-storage', default='/images', help='Directory to the images')
    args = parser.parse_args()

    # Connect to MongoDB
    load_dotenv()
    images_collection = get_mongo_collection(os.getenv('MONGO_DB_URL'), os.getenv('MONGO_DB_DATABASE'))

    pipelines = [Blip2Pipeline()]
    query_blip2 = {"$or": [{"blip2caption": {"$exists": False}}, {"blip2caption": None}]}
    size = images_collection.count_documents(query_blip2)
    counter = 0
    for image_doc in images_collection.find(query_blip2):
        counter += 1
        print(f"Processing image {counter} of {size}...")
        image_path = Path(args.image_storage).joinpath(image_doc.get("filepath"))
        if os.path.isfile(image_path):
            with Image.open(image_path) as img:
                current_img = img
                current_img_doc = image_doc
                for pipeline in pipelines:
                    print(f"{pipeline.__class__.__name__}: Processing image {image_path}...")
                    current_img, current_img_doc = pipeline.process(current_img, current_img_doc, images_collection)

    print("Done.")


def is_image_file(filepath):
    """Checks if the given file is an image based on its extension."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')
    return filepath.lower().endswith(valid_extensions)

if __name__ == "__main__":
    main()
