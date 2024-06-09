import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil
from core.query.utils.range_value_util import RangeValueUtil


class FilterWeekday(FilterBase):
    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "w" in query_parts or "wd" in query_parts:
            query_dict["weekday"] = query_parts.get("w", query_parts.get("wd"))
