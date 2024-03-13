import unittest

from core.query.filters.filter_heart_rate import FilterHeartRate


class TestFilterHeartRate(unittest.TestCase):
    def setUp(self):
        self.filter = FilterHeartRate()
        self.query = "test -h 90+-10"

    def test_remove_part_from_query(self):
        result = self.filter.remove_part_from_query(self.query)
        self.assertEqual(result, "test", "The query should be 'test' after removing the objects part")

    def test_add_to_dict(self):
        query_dict = {}
        self.filter.add_to_dict(self.query, query_dict)
        self.assertEqual(query_dict.get("heart_rate").get("min"), 80, "The min value should be 80")
        self.assertEqual(query_dict.get("heart_rate").get("max"), 100, "The max value should be 100")
