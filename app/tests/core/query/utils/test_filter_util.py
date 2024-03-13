import unittest

from core.query.utils.filter_util import FilterUtil


class TestFilterUtil(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_query_parts(self):
        query_parts = FilterUtil.parse_query_parts(
            "car|score:0.5+-0.1|position:left-bottom,car|score:0.4", "-o"
        )

        self.assertEqual(2, len(query_parts), "There should be two query_parts")
        self.assertEqual(query_parts[0]["query"], "car", "The first subquery should be 'car'")
        self.assertIn("score", query_parts[0]["subqueries"], "The first subquery should have a score")
        self.assertEqual(query_parts[0]["subqueries"]["score"]["min"], 0.4, "The first subquery should have a score min of 0.4")
        self.assertEqual(query_parts[0]["subqueries"]["score"]["max"], 0.6, "The first subquery should have a score max of 0.6")
        self.assertEqual(query_parts[0]["subqueries"]["position"], "left-bottom",
                         "The first subquery should have a position of left-bottom")

        self.assertEqual(query_parts[1]["query"], "car", "The second subquery should be 'car'")
        self.assertIn("score", query_parts[1]["subqueries"], "The second subquery should have a score")
