from time import sleep

import argparse
from dotenv import load_dotenv
import os

from core.helpers.mongo_helper import get_mongo_collection
from core.processing_pipelines.initial_pipeline import InitialPipeline
from core.processing_pipelines.open_clip_pipeline import OpenClipPipeline
from core.processing_pipelines.blip2_pipeline import Blip2Pipeline

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process an image to extract metadata and resize.")
    parser.add_argument('image_path', help='Path to the input image or a folder with images')
    parser.add_argument('--image-storage', default='/images', help='Directory to the images (the script will save images in an own folder "uploads" within that folder)')
    parser.add_argument('--upload-folder-name', default='uploads', help='Name of the subfolder where the images will be saved')
    parser.add_argument('--watch-folder', action='store_true', help='Watch the folder for new images')
    parser.add_argument('--watch-interval', type=int, default=60, help='Interval in seconds to check for new images')
    args = parser.parse_args()

    pipelines = [
        InitialPipeline(),
        OpenClipPipeline()
    ]

    # Connect to MongoDB
    load_dotenv()

    while True:
        check_images(args, pipelines)

        if not args.watch_folder:
            break

        print(f"Waiting for {args.watch_interval} seconds ...")
        sleep(args.watch_interval)

def check_images(args, pipelines):
    images_collection = get_mongo_collection(os.getenv('MONGO_DB_URL'), os.getenv('MONGO_DB_DATABASE'))

    img_paths = []

    if os.path.isdir(args.image_path):
        img_paths = [os.path.join(args.image_path, img) for img in os.listdir(args.image_path)]
    else:
        img_paths.append(args.image_path)

    for img_path in img_paths:
        if not is_image_file(img_path):
            print(f"Skipping {img_path} as it is not an image file.")
            continue
        print(f"Process {img_path} ...")
        image = None
        image_document = None
        # Extract metadata from image
        for pipeline in pipelines:
            image, image_document = pipeline.process(
                image, image_document, images_collection,
                initial_image_path=img_path,
                image_storage=args.image_storage,
                upload_folder_name=args.upload_folder_name
            )

def is_image_file(filepath):
    """Checks if the given file is an image based on its extension."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')
    return filepath.lower().endswith(valid_extensions)

if __name__ == "__main__":
    main()
