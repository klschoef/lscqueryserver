import hashlib
import json


class HashUtil:

    @staticmethod
    def hash_string(string):
        return hashlib.sha256(string.encode()).hexdigest()

    @staticmethod
    def hash_dict(dict):
        return hashlib.sha256(json.dumps(dict, sort_keys=True).encode()).hexdigest()