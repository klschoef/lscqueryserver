from core.query.subfilters.subfilter_base import SubfilterBase
from core.query.utils.range_value_util import RangeValueUtil


class SubfilterScore(SubfilterBase):
    def get_subfilter_name(self):
        return "score"

    def get_key_and_dict(self, subquery_string):
        subquery_value = self.get_subfilter_value(subquery_string)
        min_val, max_val = RangeValueUtil.parse_range_values(subquery_value)
        return self.get_subfilter_name(), {
            "min": min_val,
            "max": max_val
        }