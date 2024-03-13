import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil


class FilterObjects(FilterBase):
    REGEX = r'(-o [^\s]*)'

    """
    Remove the query part that is already handled by this filter, to avoid duplicate handling and increase performance
    If you want to keep the parts, just return the query
    """

    def remove_part_from_query(self, query):
        return re.sub(FilterObjects.REGEX, '', query).strip()

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict):
        objects = re.findall(FilterObjects.REGEX, query)
        for obj in objects:
            query_parts = FilterUtil.parse_query_parts(obj, "-o")
            if query_parts:
                query_dict["objects"] = query_dict.get("objects", []) + query_parts
