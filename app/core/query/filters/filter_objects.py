import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil


class FilterObjects(FilterBase):

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "o" in query_parts:
            query_dict["objects"] = FilterUtil.get_query_and_subqueries(query_parts, "o")
