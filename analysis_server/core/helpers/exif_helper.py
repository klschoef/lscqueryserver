import exifread
from datetime import datetime

from exifread.classes import IfdTag


def extract_exif_data(image_path):
    """Extracts EXIF metadata including creation date, latitude, and longitude."""
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    raw_printable_exif_data = {key:tags.get(key).printable for key in tags.keys() if not key.startswith("Maker") and isinstance(tags.get(key), IfdTag)}
    exif_data = {
        "datetime": None,
        "gps": {
            "latitude": None,
            "longitude": None
        }
    }

    # Extract creation datetime
    if "EXIF DateTimeOriginal" in tags:
        date_str = tags["EXIF DateTimeOriginal"].values
        exif_data["datetime"] = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

    # Extract GPS coordinates if available
    if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
        lat_ref = tags["GPS GPSLatitudeRef"].values
        lon_ref = tags["GPS GPSLongitudeRef"].values
        lat = tags["GPS GPSLatitude"].values
        lon = tags["GPS GPSLongitude"].values

        # Convert GPS coordinates to decimal format
        def convert_to_degrees(values):
            d, m, s = [float(x.num) / float(x.den) for x in values]
            return d + (m / 60.0) + (s / 3600.0)

        latitude = convert_to_degrees(lat)
        longitude = convert_to_degrees(lon)

        # Apply reference direction
        if lat_ref != "N":
            latitude = -latitude
        if lon_ref != "E":
            longitude = -longitude

        exif_data["gps"]["latitude"] = latitude
        exif_data["gps"]["longitude"] = longitude

    return exif_data, raw_printable_exif_data