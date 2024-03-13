import unittest

from core.query.utils.range_value_util import RangeValueUtil


class TestRangeValueUtil(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_range_values_with_plusminus_range(self):
        range_values = RangeValueUtil.parse_range_values("0.5+-0.1")
        self.assertEqual(range_values, (0.4, 0.6), "The range values for 0.5+-0.1 should be 0.4 and 0.6")

    def test_parse_range_values_with_min_to_infinite(self):
        range_values = RangeValueUtil.parse_range_values("0.5+")
        self.assertEqual(range_values, (0.5, None), "The range values for 0.5+ should be 0.5 and None")

    def test_parse_range_values_with_max_to_infinite(self):
        range_values = RangeValueUtil.parse_range_values("0.5-")
        self.assertEqual(range_values, (None, 0.5), "The range values for 0.5- should be 0.5 and None")

    def test_parse_range_values_with_plus_and_minus_values(self):
        range_values = RangeValueUtil.parse_range_values("0.5+0.1-0.2")
        self.assertEqual(range_values, (0.3, 0.6), "The range values for 0.5+0.1-0.2 should be 0.3 and 0.6")

    def test_parse_range_values_with_single_value(self):
        range_values = RangeValueUtil.parse_range_values("0.5")
        self.assertEqual(range_values, (0.5, 0.5), "The range values for 0.5 should be 0.5 and 0.5")