import unittest

from core.query.filters.filter_objects import FilterObjects


class TestFilterObjects(unittest.TestCase):
    def setUp(self):
        self.filter = FilterObjects()
        self.query = "test -o person|score:0.5+-0.1|position:left-bottom,car -o tree|score:0.5"

    def test_remove_part_from_query(self):
        result = self.filter.remove_part_from_query(self.query)
        self.assertEqual(result, "test", "The query should be 'test' after removing the objects part")

    def test_add_to_dict(self):
        query_dict = {}
        self.filter.add_to_dict(self.query, query_dict)
        self.assertEqual(len(query_dict.get("objects")), 3, "The query_dict should have 3 objects")
        self.assertEqual(query_dict.get("objects")[0].get("query"), "person", "The first object should be 'person'")
        self.assertEqual(query_dict.get("objects")[0].get("subqueries").get("score").get("min"), 0.4, "The first object should have a min score of 0.4")
