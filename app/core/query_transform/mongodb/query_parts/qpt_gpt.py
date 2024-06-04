import unicodedata

from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core import settings
from core.utils.solr_util import SolrUtil

"""
Transformer for GPT Description for a solr query
"""
class QPTGPT(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("gpt"))

    def needed_kwargs(self):
        return ["message"]

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        search_term = query_dict.get("gpt")
        words = search_term.split(" ")

        # Construct exact match phrase query with a boost
        exact_match_query = f'description:"{search_term}"^2.0'

        # Construct fuzzy match queries
        fuzzy_terms = [f"description:{word}~0.7" for word in words]
        fuzzy_match_query = " OR ".join(fuzzy_terms)

        # Combine exact match and fuzzy match queries
        search_query = f"{exact_match_query} OR ({fuzzy_match_query})"

        solr_url = settings.SOLR_URL
        message = kwargs.get("message")
        solr_page_size = message.get("content").get("solrPageSize") or 5000
        res = SolrUtil.search_entries(search_query, solr_url, 0, solr_page_size)
        docs = (res or {}).get("response", {}).get("docs", [])
        images = [d.get("id") for d in docs]

        mongo_query = {"filepath": {"$in": images}}

        if result_object.get("$and") is None:
            result_object["$and"] = [mongo_query]
        else:
            result_object["$and"].append(mongo_query)