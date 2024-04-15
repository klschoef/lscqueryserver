from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.query_transform.default_mongodb_sub_query_part_transformers import default_mongodb_sub_query_part_transformers


class QPTObjects(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("objects"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        object_queries = []
        for object_query in query_dict.get("objects"):
            and_query = {
                "object": object_query.get("query"),
            }

            # If there are subqueries, transform them
            if object_query.get("subqueries"):
                for key, sub_query in object_query.get("subqueries").items():
                    for transformer in default_mongodb_sub_query_part_transformers:
                        if transformer.should_use(key, sub_query):
                            transformer.transform(and_query, sub_query, *args, **kwargs)


            object_queries.append({
                "objects": {
                    "$elemMatch": and_query
                }
            })

            if result_object.get("$and") is None:
                result_object["$and"] = object_queries
            else:
                result_object["$and"] += object_queries
