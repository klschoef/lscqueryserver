import unittest

from core.query.filters.filter_base import FilterBase


class TestFilterBase(unittest.TestCase):
    def setUp(self):
        self.filter_base = FilterBase()

    def test_remove_part_from_query(self):
        query = "test query"
        result = self.filter_base.remove_part_from_query(query)
        self.assertEqual(result, query, "The query should remain the same after calling the default logic of remove_part_from_query")

    def test_add_to_dict(self):
        query = "test query"
        query_dict = {}
        self.filter_base.add_to_dict(query, query_dict)
        self.assertEqual(query_dict, {}, "The query_dict should remain the same after calling the default logic of add_to_dict")
