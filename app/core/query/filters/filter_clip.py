import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil


class FilterClip(FilterBase):
    REGEX = r'(\s-[^\s]+\s[^\s]+)' # regex to get all other filter parts with a leading -{filter_name} and a value

    """
    Remove the query part that is already handled by this filter, to avoid duplicate handling and increase performance
    If you want to keep the parts, just return the query
    """

    def remove_part_from_query(self, query):
        return query

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict):
        query = re.sub(FilterClip.REGEX, "", query).strip()
        query_dict["clip"] = query
