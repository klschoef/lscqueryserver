from datetime import datetime

import importlib

import argparse
from time import sleep

from dotenv import load_dotenv
from PIL import Image

from core.helpers.mongo_helper import get_mongo_collection
from core.processing_pipelines.blip2_pipeline import Blip2Pipeline
from pathlib import Path
import os

def to_camel_case(snake_str):
    """Convert snake_case string to CamelCase string."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def to_snake_case(camel_str):
    """Convert CamelCase string to snake_case string."""
    snake_str = ''
    for char in camel_str:
        if char.isupper():
            snake_str += '_' + char.lower()
        else:
            snake_str += char
    return snake_str.lstrip('_')

def discover_pipeline_classes(directory):
    """Discover and return all pipeline class names in a given directory."""
    class_names = []
    # List all python files in the specified directory
    for file in os.listdir(directory):
        if file.endswith("_pipeline.py"):
            # Remove '_pipeline.py' and convert to CamelCase
            base_name = file[:-3]  # remove the suffix
            class_name = to_camel_case(base_name)
            class_names.append(class_name)
    return class_names

def main():
    # Path to the directory containing pipeline modules
    pipeline_directory = 'core/processing_pipelines'
    # Discover all available class names in the pipeline directory
    available_classes = discover_pipeline_classes(pipeline_directory)
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process an image to extract metadata and resize.")
    parser.add_argument('--image-storage', default='/images', help='Directory to the images')
    parser.add_argument('--class-names', type=str, default="BlurFacesPipeline,OpenClipPipeline", help=f'Comma-separated list of pipeline class names to import and use. Available classes: {", ".join(available_classes)}')
    args = parser.parse_args()
    update_all_after_timestamp = datetime.now()

    # Connect to MongoDB
    load_dotenv()
    images_collection = get_mongo_collection(os.getenv('MONGO_DB_URL'), os.getenv('MONGO_DB_DATABASE'))

    # load pipelines
    class_names = args.class_names.split(',')
    pipelines = []
    for class_name in class_names:
        # Convert CamelCase class name back to snake_case for module name
        module_snake_name = to_snake_case(class_name)
        module_name = f'core.processing_pipelines.{module_snake_name}'
        class_module = importlib.import_module(module_name)
        class_obj = getattr(class_module, class_name)
        pipelines.append(class_obj())

    # Example of using pipelines
    print(f"Loaded {len(pipelines)} pipelines.")
    for pipeline in pipelines:
        print(f"Processing with {pipeline.__class__.__name__}")

    while True:
        error = False
        try:
            # query_blip2 = {"$or": [{"blip2caption": {"$exists": False}}, {"blip2caption": None}]}
            size = images_collection.count_documents({})
            counter = 0
            for image_doc in images_collection.find({}):
                counter += 1
                print(f"Processing image {counter} of {size}...")
                image_path = Path(args.image_storage).joinpath(image_doc.get("filepath"))
                if os.path.isfile(image_path):
                    with Image.open(image_path) as img:
                        current_img = img
                        current_img_doc = image_doc
                        for pipeline in pipelines:
                            if pipeline.should_update(current_img, current_img_doc, images_collection, update_all_after_timestamp):
                                print(f"{pipeline.__class__.__name__}: Processing image {image_path}...")
                                current_img, current_img_doc = pipeline.process(current_img, current_img_doc, images_collection)
                            else:
                                print(f"{pipeline.__class__.__name__}: Skipping image {image_path}...")
        except Exception as e:
            print(f"An error occurred: {e}")
            sleep(10)
            error = True

        if not error:
            break

    print("Done.")


def is_image_file(filepath):
    """Checks if the given file is an image based on its extension."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')
    return filepath.lower().endswith(valid_extensions)

if __name__ == "__main__":
    main()
