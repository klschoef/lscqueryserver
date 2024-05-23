from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase


class QPTCountry(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("country"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        query = {"location_metadata.country": {
            "$exists": True,
            "$regex": query_dict.get("country"),
            "$options": "i"
        }
        }

        if result_object.get("$and") is None:
            result_object["$and"] = [query]
        else:
            result_object["$and"].append(query)
