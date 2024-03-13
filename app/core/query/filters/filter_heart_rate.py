import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil
from core.query.utils.range_value_util import RangeValueUtil


class FilterHeartRate(FilterBase):
    REGEX = r'(-h [^\s]*)'
    # strings like -h 90+-10

    """
    Remove the query part that is already handled by this filter, to avoid duplicate handling and increase performance
    If you want to keep the parts, just return the query
    """

    def remove_part_from_query(self, query):
        return re.sub(FilterHeartRate.REGEX, '', query).strip()

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict):
        objects = re.findall(FilterHeartRate.REGEX, query)
        for obj in objects:
            obj = obj.strip().replace("-h ", "")
            min_val, max_val = RangeValueUtil.parse_range_values(obj)
            query_dict["heart_rate"] = {
                "min": min_val,
                "max": max_val
            }
