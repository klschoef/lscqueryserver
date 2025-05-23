from datetime import datetime

import argparse
from time import sleep

from dotenv import load_dotenv
from PIL import Image

from core.helpers.loading_helper import discover_pipeline_classes, parse_pipelines_from_string
from core.helpers.mongo_helper import get_mongo_collection
from pathlib import Path
import os

from core.helpers.parsing_helper import parse_datetime


def main():
    # Path to the directory containing pipeline modules
    pipeline_directory = 'core/processing_pipelines'
    # Discover all available class names in the pipeline directory
    available_classes = discover_pipeline_classes(pipeline_directory)
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process an image to extract metadata and resize.")
    parser.add_argument('--image-storage', default='/images', help='Directory to the images')
    parser.add_argument('--class-names', type=str, default="BlurFacesPipeline,OpenClipPipeline", help=f'Comma-separated list of pipeline class names to import and use. Available classes: {", ".join(available_classes)}')
    parser.add_argument('--update-after', type=parse_datetime, default=None, help='Update all entries after this timestamp (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM)')
    args = parser.parse_args()
    update_all_after_timestamp = args.update_after

    # Connect to MongoDB
    load_dotenv()
    images_collection = get_mongo_collection(os.getenv('MONGO_DB_URL'), os.getenv('MONGO_DB_DATABASE'))

    # load pipelines
    pipelines = parse_pipelines_from_string(args.class_names)

    # Example of using pipelines
    print(f"Loaded {len(pipelines)} pipelines.")
    for pipeline in pipelines:
        print(f"Processing with {pipeline.__class__.__name__}")

    while True:
        error = False
        try:
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
