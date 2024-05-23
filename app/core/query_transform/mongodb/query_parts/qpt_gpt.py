from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core import settings
from core.utils.solr_util import SolrUtil

"""
Transformer for GPT Description for a solr query
"""
class QPTGPT(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("gpt"))

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        search_term = query_dict.get("gpt")
        search_term = "~ ".join(search_term.split(" ")) + "~"
        search_term = f"description:({search_term})"
        solr_url = settings.SOLR_URL

        res = SolrUtil.search_entries(search_term, solr_url, 0, 10000)
        docs = (res or {}).get("response", {}).get("docs", [])
        images = [d.get("id") for d in docs]

        mongo_query = {"filepath": {"$in": images}}

        if result_object.get("$and") is None:
            result_object["$and"] = [mongo_query]
        else:
            result_object["$and"].append(mongo_query)
