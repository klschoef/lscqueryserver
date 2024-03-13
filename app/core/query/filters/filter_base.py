class FilterBase:
    """
    Remove the query part that is already handled by this filter, to avoid duplicate handling and increase performance
    If you want to keep the parts, just return the query
    """
    def remove_part_from_query(self, query):
        return query

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """
    def add_to_dict(self, query, query_dict):
        pass