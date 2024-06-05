import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil
from core.query.utils.range_value_util import RangeValueUtil


class FilterHour(FilterBase):
    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "hr" in query_parts:
            min_val, max_val = RangeValueUtil.parse_range_values(query_parts.get("hr"))
            query_dict["hour"] = {
                "min": min_val,
                "max": max_val
            }
