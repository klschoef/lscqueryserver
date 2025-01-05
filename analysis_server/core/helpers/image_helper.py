import hashlib

from PIL import Image, ExifTags
from pathlib import Path
from core.helpers.randomize_helper import generate_random_string


def resize_image(image, max_width=1024, max_height=768):
    """Resizes the image to fit within specified dimensions while maintaining aspect ratio."""
    image.thumbnail((max_width, max_height), Image.LANCZOS)
    return image


def save_image(image, output_dir, creation_date):
    """Saves the image to the specified directory with a timestamped filename."""
    timestamp_str = creation_date.strftime("%Y%m%d_%H%M%S")
    random_str = generate_random_string()
    filename = f"{timestamp_str}_{random_str}.jpg"
    output_path = get_image_storage_path(output_dir, filename)
    image.save(output_path, "JPEG", quality=30, optimize=True)
    return output_path


def get_image_storage_path(output_dir, filename):
    """Returns the path to the image in the storage directory."""
    return Path(output_dir) / filename


def open_image_with_fixed_orientation(image_path):
    """Opens an image and corrects its orientation based on EXIF data."""
    with Image.open(image_path) as img:
        # Check for EXIF data
        try:
            # Get the EXIF data
            exif = img._getexif()
            if exif is not None:
                # Iterate through EXIF data to find the orientation tag
                for tag, value in exif.items():
                    if ExifTags.TAGS.get(tag) == 'Orientation':
                        # Adjust image orientation
                        if value == 3:
                            img = img.rotate(180, expand=True)
                        elif value == 6:
                            img = img.rotate(270, expand=True)
                        elif value == 8:
                            img = img.rotate(90, expand=True)
                        break
        except (AttributeError, KeyError, IndexError):
            # No EXIF data found
            pass

        return img.copy()


def get_image_checksum(img, hash_type="sha256"):
    """
    Calculates the checksum of an already opened Pillow image.

    Parameters:
        img (PIL.Image.Image): The Pillow Image object.
        hash_type (str): The type of hash algorithm to use ('md5', 'sha1', 'sha256').

    Returns:
        str: The computed checksum in hexadecimal format.
    """
    # Initialize hash function
    hash_func = hashlib.new(hash_type)

    # Convert the image to a byte format
    img_bytes = img.tobytes()


    # Update the hash with the image bytes
    hash_func.update(img_bytes)

    return hash_func.hexdigest()

