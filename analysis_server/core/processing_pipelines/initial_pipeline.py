import os

from core.helpers.exif_helper import extract_exif_data
from core.helpers.image_helper import save_image, resize_image, open_image_with_fixed_orientation, get_image_checksum, \
    get_image_storage_path
from core.helpers.timezone_helper import get_timezone
from core.processing_pipelines.base_pipeline import BasePipeline
from datetime import datetime
from PIL import Image

class InitialPipeline(BasePipeline):
    def process(self, image, image_document, mongo_collection, remove_original_image=True, *args, **kwargs) -> tuple:
        initial_image_path, image_storage, upload_folder_name, upload_path = self.get_and_validate_kwargs(kwargs)


        exif_data, raw_exif_data = extract_exif_data(initial_image_path)
        creation_date = exif_data.get("datetime") or datetime.now()
        latitude = exif_data["gps"].get("latitude")
        longitude = exif_data["gps"].get("longitude")

        # Determine timezone if GPS data is available
        timezone = None
        if latitude and longitude:
            timezone = get_timezone(latitude, longitude)

        img = open_image_with_fixed_orientation(initial_image_path)
        # Open and resize the image
        if img:
            original_checksum = get_image_checksum(img)
            # Check if the image with this checksum already exists in the database
            existing_image_document = mongo_collection.find_one({"metadata.original_sha256_checksum": original_checksum})

            if existing_image_document:
                print(f"Image with checksum {original_checksum} already exists in the database.")
                existing_image = open_image_with_fixed_orientation(get_image_storage_path(upload_path, existing_image_document.get("filename")))
                if remove_original_image:
                    os.remove(initial_image_path)
                return existing_image, existing_image_document

            resized_img = resize_image(img)

            # Save the image with a timestamped filename
            output_path = save_image(resized_img, upload_path, creation_date)
            print(f"Image saved to {output_path}")

            # Save to mongo
            document = {
                "filename": output_path.name,
                "filepath": "/".join([upload_folder_name, output_path.name]),
                "datetime": creation_date,
                "minute_id": creation_date.strftime("%Y%m%d_%H%M"),
                "day": creation_date.day,
                "month": creation_date.month,
                "year": creation_date.year,
                "date": creation_date.strftime("%Y%m%d"),
                "weekday": creation_date.strftime("%A").lower(),
                "location": {
                    "type": "Point",
                    "coordinates": [
                        exif_data.get("gps", {}).get('longitude', 0),
                        exif_data.get("gps", {}).get('latitude', 0)
                    ]
                },
                "time_zone": timezone,
                "local_time": creation_date.strftime("%Y%m%d_%H%M"),
                "width": resized_img.size[0],
                "height": resized_img.size[1],
                "metadata": {
                    "added_to_system": datetime.now(),
                    "exif_data": raw_exif_data,
                    "original_sha256_checksum": original_checksum,
                    "resized_sha256_checksum": get_image_checksum(resized_img),
                    "original_file_name": initial_image_path.split("/")[-1],
                }
            }

            mongo_collection.insert_one(document)

            if remove_original_image:
                os.remove(initial_image_path)

            return resized_img, document
            # missing: places, concepts, objects, texts, mscaption, heart_rate, reduced, l2dist, location_metadata, gpt_description

    def get_and_validate_kwargs(self, kwargs):
        """Extracts and validates required keyword arguments."""
        initial_image_path = kwargs.get('initial_image_path')
        image_storage = kwargs.get('image_storage')
        upload_folder_name = kwargs.get('upload_folder_name')

        # Check for missing required arguments
        if not initial_image_path:
            raise ValueError("Missing required argument: 'initial_image_path' (the path to the initial image)")
        if not image_storage:
            raise ValueError("Missing required argument: 'image_storage' (where images will be stored)")

        # Validate that the initial image path exists
        if not os.path.isfile(initial_image_path):
            raise FileNotFoundError(f"The specified initial image path does not exist: {initial_image_path}")

        # Check if image_storage exists and is accessible
        if not os.path.isdir(image_storage):
            raise FileNotFoundError(f"The specified image storage directory does not exist or is not accessible: {image_storage}")

        # Combine image_storage with upload_folder_name to create the full upload path
        upload_path = os.path.join(image_storage, upload_folder_name)

        # Ensure the upload directory exists within image storage or create it if necessary
        if not os.path.isdir(upload_path):
            os.makedirs(upload_path, exist_ok=True)

        return initial_image_path, image_storage, upload_folder_name, upload_path
