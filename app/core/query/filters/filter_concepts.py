import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil


class FilterConcepts(FilterBase):
    def add_to_dict(self, query, query_dict, query_parts):
        if "c" in query_parts:
            query_dict["concepts"] = FilterUtil.get_query_and_subqueries(query_parts, "c")
