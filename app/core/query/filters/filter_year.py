import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil
from core.query.utils.range_value_util import RangeValueUtil


class FilterYear(FilterBase):
    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "y" in query_parts:
            query_dict["year"] = query_parts.get("y")
