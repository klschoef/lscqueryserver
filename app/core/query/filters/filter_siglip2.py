from core.query.filters.filter_base import FilterBase


class FilterSigLIP2(FilterBase):
    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict, query_parts):
        if "siglip2" in query_parts:
            query_dict["siglip2"] = {"query": query_parts["siglip2"], "subqueries": {}}

