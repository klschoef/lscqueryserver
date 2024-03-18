from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.query_transform.default_mongodb_sub_query_part_transformers import default_mongodb_sub_query_part_transformers


class QPTTexts(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("texts"))

    def transform(self, result_object, query_dict, *args, **kwargs):
        text_queries = []
        for text_query in query_dict.get("texts"):
            and_query = {
                "text": {"$regex": text_query.get("query"), "$options": "i"}
            }

            # If there are subqueries, transform them
            if text_query.get("subqueries"):
                for key, sub_query in text_query.get("subqueries").items():
                    for transformer in default_mongodb_sub_query_part_transformers:
                        if transformer.should_use(key, sub_query):
                            transformer.transform(and_query, sub_query, *args, **kwargs)


            text_queries.append({
                "texts": {
                    "$elemMatch": and_query
                }
            })

            if result_object.get("$and") is None:
                result_object["$and"] = text_queries
            else:
                result_object["$and"] += text_queries
