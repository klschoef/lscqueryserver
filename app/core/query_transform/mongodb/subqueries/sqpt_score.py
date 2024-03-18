from core.query_transform.base.subqueries.sub_query_part_transformer_base import SubQueryPartTransformerBase


class SQPTScore(SubQueryPartTransformerBase):

    def should_use(self, key, sub_query):
        return key == "score"

    def transform(self, result_object, sub_query, *args, **kwargs):
        result_object["score"] = {}
        if sub_query.get("min"):
            result_object["score"]["$gte"] = sub_query.get("min")
        if sub_query.get("max"):
            result_object["score"]["$lte"] = sub_query.get("max")
