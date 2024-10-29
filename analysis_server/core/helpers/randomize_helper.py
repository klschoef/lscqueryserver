import random
import string

def generate_random_string(length=6):
    """Generates a random string for unique filename suffix."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))