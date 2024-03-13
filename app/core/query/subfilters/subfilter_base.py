class SubfilterBase:

    """
    Returns the name of the subfilter. Like "score" for the score subfilter.
    """
    def get_subfilter_name(self):
        return None

    def get_subfilter_value(self, subquery_string):
        return subquery_string[len(self.get_subfilter_name() or "") + 1:]

    """
    Returns if the subfilter should be used.
    Input: subquery_string: string like "score:0.5+-0.1". Format: [subfilter_name]:[value]
    """
    def should_be_used(self, subquery_string):
        return subquery_string.startswith(f"{self.get_subfilter_name()}:")

    """
    Returns a key and a dictionary with the subfilter value.
    Input: subquery_string: string like "score:0.5+-0.1". Format: [subfilter_name]:[value]
    """
    def get_key_and_dict(self, subquery_string):
        return None, None