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
        search_term = query_dict.get("gpt").strip()
        words = search_term.split(" ")

        # Identify inclusion and exclusion terms
        include_words = [word for word in words if not word.startswith("!")]
        exclude_words = [word[1:] for word in words if word.startswith("!")]

        # Construct exact match phrase query with a boost
        exact_match_query = f'description:"{" ".join(include_words)}"^2.0'

        # Construct fuzzy match queries
        fuzzy_terms = [f"description:{word}~0.7" for word in include_words]
        fuzzy_match_query = " OR ".join(fuzzy_terms)

        # Construct exclude queries
        exclude_queries = [f"-description:{word}" for word in exclude_words]
        exclude_query = " AND ".join(exclude_queries)

        # Combine exact match, fuzzy match, and exclude queries
        if exclude_query:
            search_query = f"({exact_match_query} OR ({fuzzy_match_query})) AND {exclude_query}"
        else:
            search_query = f"({exact_match_query} OR ({fuzzy_match_query}))"

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

