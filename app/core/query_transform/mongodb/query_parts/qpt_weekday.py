from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.query_transform.default_mongodb_sub_query_part_transformers import default_mongodb_sub_query_part_transformers


class QPTWeekday(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("weekday"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        query = {"weekday": query_dict.get("weekday")}

        if result_object.get("$and") is None:
            result_object["$and"] = [query]
        else:
            result_object["$and"].append(query)
