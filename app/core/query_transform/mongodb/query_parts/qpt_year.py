from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.query_transform.default_mongodb_sub_query_part_transformers import default_mongodb_sub_query_part_transformers


class QPTYear(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("year"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        year = query_dict.get("year")
        result_object["year"] = {}
        if year.get("min"):
            result_object["year"]["$gte"] = year.get("min")
        if year.get("max"):
            result_object["year"]["$lte"] = year.get("max")
