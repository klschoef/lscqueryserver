import json
import datetime

from bson import ObjectId


"""
Serialize a value to a json serializable value, if it is not already json serializable
"""
class ObjectSerializer:

    """
    Serialize a value to a json serializable value, if it is not already json serializable
    """
    @staticmethod
    def serialize_value(value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, dict):
            return ObjectSerializer.object_to_serialized_json(value)
        elif isinstance(value, list):
            return ObjectSerializer.objects_to_serialized_json(value)
        return value

    @staticmethod
    def object_to_serialized_json(obj):
        if isinstance(obj, list):
            return ObjectSerializer.objects_to_serialized_json(obj)
        if not isinstance(obj, dict):
            return obj

        for key, value in obj.items():
           obj[key] = ObjectSerializer.serialize_value(value)
        return obj

    @staticmethod
    def objects_to_serialized_json(objects):
        if isinstance(objects, dict):
            return ObjectSerializer.object_to_serialized_json(objects)
        if not isinstance(objects, list):
            return objects
        return [ObjectSerializer.object_to_serialized_json(obj) for obj in objects]