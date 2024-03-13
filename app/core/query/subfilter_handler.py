from core.query.default_subfilters import default_subfilters


class SubfilterHandler:

    """
    This class is responsible for handling subfilters, based on the default_subfilter list.
    You also can define a custom subfilter list.
    Input:
    - subquery_string: string like "score:0.5+-0.1". Format: [subfilter_name]:[value]
    """
    @staticmethod
    def subfilter_handler(subquery_string, subfilters=default_subfilters):
        for subfilter_obj in subfilters:
            if subfilter_obj.should_be_used(subquery_string):
                return subfilter_obj.get_key_and_dict(subquery_string)
        return None, None