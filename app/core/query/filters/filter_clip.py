import re

from core.query.filters.filter_base import FilterBase


class FilterClip(FilterBase):
    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "clip" in query_parts:
            query_dict["clip"] = {"query": query_parts["clip"], "subqueries": {}}
