import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil
from core.query.utils.range_value_util import RangeValueUtil


class FilterDay(FilterBase):
    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "d" in query_parts:
            query_dict["day"] = query_parts.get("d")
