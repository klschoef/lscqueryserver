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

    def parse_weighted_terms(self, search_term):
        terms = search_term.split()
        include_terms = []
        exclude_terms = []

        for term in terms:
            if term.startswith("!"):
                exclude_terms.append(term[1:])
            elif ":" in term:
                word, weight = term.split(":")
                include_terms.append((word, float(weight)))
            else:
                include_terms.append((term, 1.0))

        return include_terms, exclude_terms

    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        search_term = query_dict.get("gpt").strip()
        include_terms, exclude_terms = self.parse_weighted_terms(search_term)

        # Construct exact match and fuzzy match queries
        exact_match_queries = [f'description:"{term}"^{weight}' for term, weight in include_terms]
        fuzzy_match_queries = [f"description:{term}~0.7^{weight}" for term, weight in include_terms]

        # Combine exact match and fuzzy match queries
        exact_match_query = " OR ".join(exact_match_queries)
        fuzzy_match_query = " OR ".join(fuzzy_match_queries)

        # Construct exclude queries
        exclude_queries = [f"-description:{term}" for term in exclude_terms]
        exclude_query = " AND ".join(exclude_queries)

        # Combine all queries
        if exclude_query:
            search_query = f"({exact_match_query} OR {fuzzy_match_query}) AND {exclude_query}"
        else:
            search_query = f"({exact_match_query} OR {fuzzy_match_query})"

        solr_url = settings.SOLR_URL
        solr_core = kwargs.get("message", {}).get("content", {}).get("solrCore", settings.SOLR_DEFAULT_CORE)
        solr_url = f"{solr_url}/{solr_core}"
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
