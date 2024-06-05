from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase

class QPTHour(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("hour"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        hour = query_dict.get("hour")
        result_object["hour"] = {}
        if hour.get("min"):
            result_object["hour"]["$gte"] = hour.get("min")
        if hour.get("max"):
            result_object["hour"]["$lte"] = hour.get("max")
