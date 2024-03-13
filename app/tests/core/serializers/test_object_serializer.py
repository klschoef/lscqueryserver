import unittest
import json
import datetime
from pathlib import Path

from bson import ObjectId

from core.serializers.object_serializer import ObjectSerializer
from tests.mock_data.mock_loader import MockLoader


class TestObjectSerializer(unittest.TestCase):
    def setUp(self):
        self.data = MockLoader.load("mongo_responses/first_10_images_all_fields.json")

    def test_serialize_value(self):
        # Test serialization of datetime
        dt = datetime.datetime.now()
        self.assertEqual(ObjectSerializer.serialize_value(dt), dt.isoformat())

        # Test serialization of ObjectId
        oid = ObjectId()
        self.assertEqual(ObjectSerializer.serialize_value(oid), str(oid))

        # Test serialization of dict
        dict_val = {"key": "value"}
        self.assertEqual(ObjectSerializer.serialize_value(dict_val), {"key": "value"})

        # Test serialization of list
        list_val = ["value1", "value2"]
        self.assertEqual(ObjectSerializer.serialize_value(list_val), ["value1", "value2"])

    def test_object_to_serialized_json(self):
        for obj in self.data:
            serialized_obj = ObjectSerializer.object_to_serialized_json(obj)
            self.assertIsInstance(serialized_obj, dict)

    def test_objects_to_serialized_json(self):
        serialized_objects = ObjectSerializer.objects_to_serialized_json(self.data)
        self.assertIsInstance(serialized_objects, list)
        for obj in serialized_objects:
            self.assertIsInstance(obj, dict)