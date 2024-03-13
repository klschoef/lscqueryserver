from core.query.subfilters.subfilter_base import SubfilterBase


class SubfilterPosition(SubfilterBase):
    def get_subfilter_name(self):
        return "position"

    def get_key_and_dict(self, subquery_string):
        return self.get_subfilter_name(), self.get_subfilter_value(subquery_string)