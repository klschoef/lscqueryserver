from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase

class QPTHeartRate(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("heart_rate"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        heart_rate = query_dict.get("heart_rate")
        result_object["heart_rate"] = {}
        if heart_rate.get("min"):
            result_object["heart_rate"]["$gte"] = heart_rate.get("min")
        if heart_rate.get("max"):
            result_object["heart_rate"]["$lte"] = heart_rate.get("max")
