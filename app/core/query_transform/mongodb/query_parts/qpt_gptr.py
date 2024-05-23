from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase


"""
Transformer for GPT Description for a regex query
"""
class QPTGPTR(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("gptr"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        query = {"gpt_description.description": {
            "$exists": True,
            "$regex": query_dict.get("gptr"),
            "$options": "i"
        }
        }

        if result_object.get("$and") is None:
            result_object["$and"] = [query]
        else:
            result_object["$and"].append(query)
