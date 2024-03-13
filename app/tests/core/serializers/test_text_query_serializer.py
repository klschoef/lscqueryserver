import unittest

from core.serializers.text_query_serializer import TextQuerySerializer


class TestTextQquerySerializer(unittest.TestCase):
    def setUp(self):
        pass

    def test_text_query_to_dict(self):
        query_dict = TextQuerySerializer.text_query_to_dict("test -o person|score:0.5+-0.1|position:left-bottom,car -o tree|score:0.5")
        self.assertEqual(query_dict.get("objects")[0].get("query"), "person", "The first object should be 'person'")
        self.assertEqual(query_dict.get("objects")[0].get("subqueries").get("score").get("min"), 0.4, "The first object should have a min score of 0.4")

    def test_text_query_to_dict_with_heart_rate(self):
        query_dict = TextQuerySerializer.text_query_to_dict("test -o person -h 90+-5")
        self.assertEqual(query_dict.get("objects")[0].get("query"), "person", "The first object should be 'person'")
        self.assertEqual(query_dict.get("heart_rate").get("min"), 85, "The heart rate should be 85")
        self.assertEqual(query_dict.get("heart_rate").get("max"), 95, "The heart rate should be 95")