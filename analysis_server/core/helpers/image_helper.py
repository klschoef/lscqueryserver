from PIL import Image
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
    output_path = Path(output_dir) / filename
    image.save(output_path, "JPEG", quality=30, optimize=True)
    return output_path