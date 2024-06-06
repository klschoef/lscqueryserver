from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.query_transform.default_mongodb_sub_query_part_transformers import default_mongodb_sub_query_part_transformers


class QPTDay(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("day"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        day = query_dict.get("day")
        result_object["day"] = {}
        if day.get("min"):
            result_object["day"]["$gte"] = day.get("min")
        if day.get("max"):
            result_object["day"]["$lte"] = day.get("max")
