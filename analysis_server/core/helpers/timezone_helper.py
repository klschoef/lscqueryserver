from timezonefinder import TimezoneFinder


def get_timezone(latitude, longitude):
    """Infers the timezone based on GPS coordinates."""
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lat=latitude, lng=longitude)
    return timezone