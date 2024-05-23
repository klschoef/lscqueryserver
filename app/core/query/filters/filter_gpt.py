import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil


class FilterGPT(FilterBase):
    REGEX = r'(-gpt [^\s]*)'

    """
    Remove the query part that is already handled by this filter, to avoid duplicate handling and increase performance
    If you want to keep the parts, just return the query
    """

    def remove_part_from_query(self, query):
        return re.sub(FilterGPT.REGEX, '', query).strip()

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict):
        gpts = re.findall(FilterGPT.REGEX, query)
        for gpt in gpts:
            query_parts = FilterUtil.parse_query_parts(gpt, "-gpt")
            if query_parts:
                gpt_query = (query_parts[0] if len(query_parts) > 0 else {}).get("query")
                if gpt_query:
                    query_dict["gpt"] = gpt_query
