from datetime import datetime


def parse_datetime(datetime_string):
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(datetime_string, fmt)
        except ValueError:
            pass
    raise ValueError("No valid date format found for input")