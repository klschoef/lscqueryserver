from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.query_transform.default_mongodb_sub_query_part_transformers import default_mongodb_sub_query_part_transformers


class QPTMonth(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("month"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        month = query_dict.get("month")
        result_object["month"] = {}
        if month.get("min"):
            result_object["month"]["$gte"] = month.get("min")
        if month.get("max"):
            result_object["month"]["$lte"] = month.get("max")
